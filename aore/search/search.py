import re
import time
from typing import Tuple, List

import Levenshtein
import asyncpg
import sphinxapi

from .wordentry import WordEntry
from .wordvariation import VariationType
from .. import log
from ..exceptions import FiasBadDataException, FiasNotFoundException
from ..schemas import AoResultItemModel
from settings import AppConfig
from ..utils.search import trigram, violet_ratio


def _parse_sphinx_address(addr: str) -> Tuple[str, int | None]:
    """
    Получает параметры подключения для Sphinx (хост и порт) по строке
    :param addr: адрес однной строкой
    :return: хост и порт
    """
    if ":" in addr and "unix:/" not in addr:
        sphinx_host, sphinx_port = addr.split(":")
        return sphinx_host, int(sphinx_port)

    return addr, None


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
    conf: AppConfig.Shpinx
    client_sugg: sphinxapi.SphinxClient  # клиент для подсказок
    client_show: sphinxapi.SphinxClient  # клиент для поиска адреса

    def __init__(self, pool: asyncpg.Pool, conf: AppConfig.Shpinx) -> None:
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

    def __configure(self, index_name: str, word_len: int) -> None:
        self.client_sugg.ResetFilters()

        if index_name == self.conf.index_sugg:
            self.client_sugg.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
            self.client_sugg.SetFilterRange("len", int(word_len) - self.conf.delta_len,
                                            int(word_len) + self.conf.delta_len)
            self.client_sugg.SetSelect(f"word, len, @weight+{self.conf.delta_len}-abs(len-{word_len}) AS krank")
            self.client_sugg.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")
        else:
            self.client_show.SetRankingMode(sphinxapi.SPH_RANK_BM25)
            self.client_show.SetSelect("aoid, fullname, @weight-2*abs(wordcount-{}) AS krank".format(word_len))
            self.client_show.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")

    def __get_suggestions(self, word: str, rating_limit: float, count: int) -> List[WordEntry.SuggEntity]:
        # настраиваем клиента Sphinx
        self.__configure(self.conf.index_sugg, len(word))
        result = self.client_sugg.Query(f'"{trigram(word)}"/1', self.conf.index_sugg)

        # Если по данному слову не найдено подсказок (а такое бывает?), возвращаем []
        if not result['matches']:
            return []

        maxrank: int = result['matches'][0]['attrs']['krank']
        print(f'maxrank {maxrank} type={type(maxrank)}')  # TODO: check is really int, remove if none
        maxleven: float | None = None

        outlist: List[WordEntry.SuggEntity] = []
        for match in result['matches']:
            if len(outlist) >= count:
                break

            if maxrank - match['attrs']['krank'] < self.conf.default_rating_delta:
                jaro_rating: float = Levenshtein.jaro(word, match['attrs']['word'])
                if not maxleven:
                    maxleven = jaro_rating - jaro_rating * self.conf.regression_coef
                if jaro_rating >= rating_limit and jaro_rating >= maxleven:
                    outlist.append(WordEntry.SuggEntity(word=match['attrs']['word'], jaro=jaro_rating))

        outlist.sort(key=lambda x: x.jaro, reverse=True)

        return outlist

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
        all_variations = []
        for word_entry in word_entries:
            for variation in word_entry.generate_variations(self.conf, strong, self.__get_suggestions):
                all_variations.append(variation)
        elapsed_get_variations = time.time() - start_t

        # делим на плохие (частые) и хорошие (полное слово, редкие) вариации слов
        good_vars = [v for v in all_variations if v.var_type == VariationType.NORM]
        freq_vars = [v for v in all_variations if v.var_type == VariationType.FREQ]

        good_vars_word_count = len(set([v.parent for v in good_vars]))
        freq_vars_word_count = len(set([v.parent for v in freq_vars]))

        # настраиваем основной клиент (для поиска главной фразы)
        self.__configure(self.conf.index_addrobj, word_count)

        # формируем строки для поиска в Сфинксе
        for i in range(good_vars_word_count, max(0, good_vars_word_count - 3), -1):
            first_q = "@fullname \"{}\"/{}".format(" ".join(good_var.text for good_var in good_vars), i)
            if self.conf.search_freq_words and freq_vars_word_count > 0:
                second_q = " @sname {}".format(" ".join(freq_var.text for freq_var in freq_vars))
                self.client_show.AddQuery(first_q + second_q, self.conf.index_addrobj)

            self.client_show.AddQuery(first_q, self.conf.index_addrobj)

        start_t = time.time()
        rs = self.client_show.RunQueries()
        elapsed_run_queries = time.time() - start_t

        log.debug(f"FIND: '{text}', vari_t={elapsed_get_variations}, q_t={elapsed_run_queries}")

        if rs is None:
            raise FiasNotFoundException("Cannot find address text")

        results: List[AoResultItemModel] = []
        parsed_ids: List[str] = []

        for i in range(0, len(rs)):
            for match in rs[i]['matches']:
                if len(results) >= self.conf.max_results_count:
                    log.debug(f'Breaking on {len(results)} >= {self.conf.max_results_count}')
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

        # При строгом поиске нам надо еще добавить fuzzy и выбрать самое большое значение при отклонении
        # выше заданного, по сути переопределяем ratio
        if strong:
            for result in results:
                result.ratio = violet_ratio(text, result.text.lower())

            # Сортируем по убыванию признака
            results.sort(key=lambda x: x.ratio, reverse=True)

            # Если подряд два одинаково релеватных результата - это плохо, на автомат такое отдавать нельзя
            if len(results) >= 2 and abs(results[0].ratio - results[1].ratio) == 0.0:
                log.warn(f'Found 2 matches with close ratio: {results[0]} and {results[1]}')
                raise FiasNotFoundException("Found 2 very close matches")
            else:
                # Возвращаем первый сверху результат
                results = [results[0]]

        return results
