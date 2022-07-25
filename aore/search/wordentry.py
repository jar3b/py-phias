import json
import re
from dataclasses import dataclass
from typing import cast, List, Iterator, Callable, Tuple

import asyncpg
from jinja2 import Environment, FileSystemLoader

from aore.search.wordvariation import WordVariation
from settings import AppConfig
from .match_types import MatchTypes
from .ranks_data import RanksData


def _cleanup_string(word: str) -> str:
    return word.replace('-', '').replace('@', '').replace('#', '')


class WordEntry:
    __slots__ = ['bare_word', 'word', 'is_freq', 'socr_word', 'is_initialized', 'mt']

    bare_word: str  # слово без стрипаных символов
    word: str  # слово уже трипнутое
    is_freq: bool | None  # это часто используемое слово
    socr_word: str | None  # это сокращенное слово
    is_initialized: bool  # объект инициализирован или нет
    mt: set[MatchTypes]  # параметры

    @dataclass
    class SuggEntity:
        word: str
        jaro: float
        freq: int
        precision: float

    def __init__(self, word: str) -> None:
        self.bare_word = word
        self.word = _cleanup_string(self.bare_word)
        self.is_freq = None
        self.socr_word = None
        self.mt = set()

        self.is_initialized = False

    async def init(self, rank_data: RanksData, conf: AppConfig.Sphinx) -> None:
        self.socr_word = rank_data.scname
        self.is_freq = rank_data.is_freq

        # Заполняем параметры слова
        mt_entry: MatchTypes
        for mt_entry in MatchTypes:
            for mt_value in cast(List[str], mt_entry.value):
                if mt_entry in self.mt or re.search(mt_value, rank_data.rank):
                    self.mt.add(mt_entry)

        # Строка слишком котроткая, то по лайку не ищем, сфинкс такого не прожует
        if MatchTypes.MT_LAST_STAR in self.mt and len(self.word) < conf.min_length_to_star:
            self.mt.discard(MatchTypes.MT_LAST_STAR)
            self.mt.add(MatchTypes.MT_AS_IS)

        # Если звездочки с двух сторон, то с одной убираем
        if MatchTypes.MT_BOTH_STAR in self.mt:
            self.mt.discard(MatchTypes.MT_LAST_STAR)

        # Теперь модель иницилизирована
        self.is_initialized = True

    def generate_variations(
            self,
            conf: AppConfig.Sphinx,
            strong: bool,
            suggestion_func: Callable[[str, float, int], List[SuggEntity]]
    ) -> Iterator[
        WordVariation
    ]:
        # Если слово встречается часто, ставим у всех вариантов тип VariationType.freq
        socr_words: List[Tuple[str, float]] = []
        full_words: List[Tuple[str, float]] = []

        # Добавляем подсказки (много штук)
        if (MatchTypes.MT_MANY_SUGG in self.mt or MatchTypes.MT_SOME_SUGG in self.mt) and not strong:
            max_s = 1
            second_s = 0
            for suggestion in suggestion_func(self.word, conf.rating_limit_soft, conf.rating_limit_soft_count):
                if int(suggestion.freq) > 30000:
                    max_s = max(max_s, int(suggestion.freq))
                    socr_words.append((suggestion.word, 1))
                else:
                    second_s = max(second_s, int(suggestion.freq))
                    full_words.append((suggestion.word, round(suggestion.precision - 0.2, 2)))

            # Если самое частое слово прям намного чаще чем остальные - отбрасываем их
            if second_s / max_s < 0.001:
                full_words = []

            # Если всего одно слово в предложении, ставим бустер в 0.9
            if len(full_words) == 1:
                full_words[0] = (full_words[0][0], 0.9)

        # Добавляем звездочку на конце
        if MatchTypes.MT_LAST_STAR in self.mt and not self.is_freq:
            full_words.append((f'{self.word}*', 0.9))

        # Добавляем звездочки с двух сторон TODO: Для теста с одной
        if MatchTypes.MT_BOTH_STAR in self.mt and not self.is_freq:
            full_words.append((f'{self.word}*', 0.9))

        # Добавляем слово "как есть", если это сокращение, то добавляем как частое слово
        if MatchTypes.MT_AS_IS in self.mt:
            if self.is_freq or MatchTypes.MT_IS_SOCR in self.mt:
                socr_words.append((self.bare_word if MatchTypes.MT_IS_SOCR else self.word, 1))

            if MatchTypes.MT_IS_SOCR not in self.mt:
                full_words.append((self.word, 1))

        # Добавляем сокращение
        if MatchTypes.MT_ADD_SOCR in self.mt and self.socr_word:
            socr_words.append((self.socr_word, 1))

        yield WordVariation(self, full_words, socr_words)

    @classmethod
    async def fill(cls, entries: List['WordEntry'], *, pool: asyncpg.Pool, conf: AppConfig.Sphinx) -> None:
        env = Environment(loader=FileSystemLoader('aore/templates'))
        query_ranks = env.get_template('query_ranks.sql').render()

        data = [{'w': w.word, 'bare': w.bare_word} for w in entries]

        async with pool.acquire() as conn:
            records = await conn.fetch(
                query_ranks,
                json.dumps(data)
            )

        ranks_data = {r['w']: RanksData.load(r['json_agg']) for r in records}
        for w in entries:
            await w.init(ranks_data[w.word], conf)

    def __str__(self) -> str:
        return self.word
