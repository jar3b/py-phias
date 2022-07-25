import re
import time
from collections import OrderedDict
from typing import Tuple, List

import asyncpg
import sphinxapi

from settings import AppConfig
from .query_generator import SearchQueryGenerator
from .wordentry import WordEntry
from .wordvariation import WordVariation
from .. import log
from ..exceptions import FiasBadDataException, FiasNotFoundException
from ..schemas import AoResultItemModel
from ..utils.search import trigram


def _parse_sphinx_address(addr: str) -> Tuple[str, int | None]:
    """
    Получает параметры подключения для Sphinx (хост и порт) по строке
    :param addr: адрес однной строкой
    :return: хост и порт
    """
    if ":" in addr:
        sphinx_host, sphinx_port = addr.split(":")
        return sphinx_host, int(sphinx_port)

    return 'unix://' + addr, None


def _split_phrase(phrase: str) -> List[str]:
    """
    Бьект строку (адресную строку) по разделителям
    :param phrase: исходная строка
    :return: массив слов
    """
    phrase = phrase.lower()
    return re.split(r"[ ,:.#$]+", phrase)


class SphinxSearch:
    __slots__ = ['pool', 'conf', 'client_sugg', 'client_show']

    pool: asyncpg.Pool
    conf: AppConfig.Sphinx
    client_sugg: sphinxapi.SphinxClient  # клиент для подсказок
    client_show: sphinxapi.SphinxClient  # клиент для поиска адреса

    def __init__(self, pool: asyncpg.Pool, conf: AppConfig.Sphinx) -> None:
        self.pool = pool
        self.conf = conf

        sphinx_host, sphinx_port = _parse_sphinx_address(conf.listen)

        # Настраиваем подключение для подсказок
        self.client_sugg = sphinxapi.SphinxClient()
        self.client_sugg.SetServer(sphinx_host, sphinx_port)
        self.client_sugg.SetLimits(0, conf.max_results_count)
        self.client_sugg.SetConnectTimeout(3.0)

        # Настраиваем подключение для поиска адреса
        self.client_show = sphinxapi.SphinxClient()
        self.client_show.SetServer(sphinx_host, sphinx_port)
        self.client_show.SetLimits(0, conf.max_results_count)
        self.client_show.SetConnectTimeout(3.0)

    def __configure(self, index_name: str, word_len: int, main_ranker: int = sphinxapi.SPH_RANK_BM25) -> None:
        self.client_sugg.ResetFilters()

        if index_name == self.conf.index_sugg:
            self.client_sugg.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
            self.client_sugg.SetFilterRange("len", int(word_len) - self.conf.delta_len,
                                            int(word_len) + self.conf.delta_len)
            self.client_sugg.SetSelect(
                f"word, len, frequency, @weight+{self.conf.delta_len}-abs(len-{word_len}) AS krank")
            self.client_sugg.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")
        else:
            self.client_show.SetRankingMode(main_ranker)
            self.client_show.SetSelect(f"aoid, fullname, @weight-4*abs(wordcount-{word_len}) AS krank")
            self.client_show.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")

    # TODO: rating_limit больше не используется, потом  надо будет убрать, но возможно новая версия ищет хуже
    def __get_suggestions(self, word: str, rating_limit: float, count: int) -> List[WordEntry.SuggEntity]:
        # настраиваем клиента Sphinx
        self.__configure(self.conf.index_sugg, len(word))
        result = self.client_sugg.Query(f'"{trigram(word)}"/1', self.conf.index_sugg)

        if result is None:
            raise FiasNotFoundException("Cannot find address sub-text")

        # Если по данному слову не найдено подсказок (а такое бывает?), возвращаем []
        if not result['matches']:
            return []

        max_rank: int = result['matches'][0]['attrs']['krank']

        suggestions = sorted([
            WordEntry.SuggEntity(
                word=match['attrs']['word'],
                jaro=match['attrs']['krank'],
                freq=match['attrs']['frequency'],
                precision=match['attrs']['krank'] / max_rank
            ) for match in result['matches'] if max_rank - match['attrs']['krank'] < self.conf.default_rating_delta
        ], key=lambda x: x.jaro, reverse=True)

        sugg_perfect = [x for x in suggestions if x.precision == 1]
        if len(sugg_perfect) >= 2:
            return sugg_perfect[:count]
        return suggestions[:count]

    # Получает список объектов (слово)
    async def __get_word_entries(self, words: List[str]) -> List[WordEntry]:
        word_entries = [WordEntry(w) for w in words if w != '']
        await WordEntry.fill(word_entries, pool=self.pool, conf=self.conf)

        return word_entries

    # Осуществляет поиск строки
    async def find(self, text: str, strong: bool) -> List[AoResultItemModel]:
        # сплитим текст на слова
        words = _split_phrase(text)

        # получаем список объектов (слов)
        word_entries = await self.__get_word_entries(words)
        word_count = len(word_entries)

        # проверяем, есть ли вообще что-либо в списке объектов слов (или же все убрали как частое)
        if word_count == 0:
            raise FiasBadDataException("No legal words is specified")

        # получаем все вариации слов
        start_t = time.time()
        # Тут OrderedDict, чтобы отсеять одинаковые слова
        all_variations_dict: OrderedDict[WordVariation, None] = OrderedDict()
        for word_entry in word_entries:
            for variation in word_entry.generate_variations(self.conf, strong, self.__get_suggestions):
                all_variations_dict[variation] = None
        all_variations = list(all_variations_dict.keys())
        elapsed_get_variations = time.time() - start_t

        # Если поиск строгий, то нет подсказок, и может быть такое, что слово будет пустым. Так нельзя
        if strong and any([x.is_empty for x in all_variations]):
            raise FiasNotFoundException("Got empty word with strong search")

        has_socr = any([v.has_short_words for v in all_variations])

        # настраиваем основной клиент (для поиска главной фразы), если строгий поиск - то учитываем длизость слов
        self.__configure(
            self.conf.index_addrobj,
            word_count,
            sphinxapi.SPH_RANK_PROXIMITY_BM25 if strong else sphinxapi.SPH_RANK_BM25
        )

        # формируем строки для поиска в Сфинксе
        gen = SearchQueryGenerator(all_variations)
        all_queries = OrderedDict()
        ops = ['']
        if not strong:
            ops.append('MAYBE')

        for operation in ops:
            if self.conf.search_freq_words and has_socr:
                all_queries[gen.get_query(op=operation, with_short=True)] = None
            all_queries[gen.get_query(op=operation, with_short=False)] = None

        # добавляем все квери, убирая дубликаты
        for k in all_queries.keys():
            self.client_show.AddQuery(k, self.conf.index_addrobj)

        start_t = time.time()
        rs = self.client_show.RunQueries()
        elapsed_run_queries = time.time() - start_t

        log.debug(f"FIND: '{text}', vari_t={elapsed_get_variations}, q_t={elapsed_run_queries}")

        if rs is None:
            raise FiasNotFoundException("Cannot find address text")

        results: List[AoResultItemModel] = []
        parsed_ids: List[str] = []

        for i in range(0, len(rs)):
            if rs[i].get('error', None):
                log.error(f'Invalid query: {rs[i]["error"].decode("utf-8")}')
                raise FiasNotFoundException("Error searching address text")

            for match in rs[i].get('matches', ()):
                if len(results) >= self.conf.max_results_count:
                    break

                if not match['attrs']['aoid'] in parsed_ids:
                    parsed_ids.append(match['attrs']['aoid'])
                    results.append(
                        AoResultItemModel(
                            aoid=match['attrs']['aoid'],
                            text=str(match['attrs']['fullname']),
                            ratio=match['attrs']['krank'],
                            cort=i
                        )
                    )

        # Доп обработка при строгом поиске, даем ошибку при похожих результатах
        if strong:
            if not results:
                raise FiasNotFoundException("No match for strong search")

            # Если подряд два одинаково релеватных результата - это плохо, на автомат такое отдавать нельзя
            if len(results) >= 2 and abs(results[0].ratio - results[1].ratio) == 0.0:
                log.warn(f'Found 2 matches with close ratio: {results[0]} and {results[1]}')
                raise FiasNotFoundException("Found 2 very close matches")
            else:
                # Возвращаем первый сверху результат
                results = [results[0]]

        return results
