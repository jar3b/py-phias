import json
import re
from dataclasses import dataclass
from typing import cast, List, Iterator, Callable

import asyncpg
from jinja2 import Environment, FileSystemLoader

from aore.search.wordvariation import WordVariation, VariationType
from .match_types import MatchTypes
from .ranks_data import RanksData
from settings import AppConfig


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

        # Если ищем по лайку, то точное совпадение не ищем (оно и так будет включено)
        if MatchTypes.MT_LAST_STAR in self.mt:
            self.mt.discard(MatchTypes.MT_AS_IS)

        # Строка слишком котроткая, то по лайку не ищем, сфинкс такого не прожует
        if MatchTypes.MT_LAST_STAR in self.mt and len(self.word) < conf.min_length_to_star:
            self.mt.discard(MatchTypes.MT_LAST_STAR)
            self.mt.add(MatchTypes.MT_AS_IS)

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
        variation_type = VariationType.FREQ if self.is_freq else VariationType.NORM

        # Добавляем подсказки (много штук)
        if MatchTypes.MT_MANY_SUGG in self.mt and not strong:
            suggs = suggestion_func(self.word, conf.rating_limit_soft, conf.rating_limit_soft_count)
            for suggestion in suggs:
                yield WordVariation(self, suggestion.word, variation_type)

        # Добавляем подсказки (немного)
        if MatchTypes.MT_SOME_SUGG in self.mt and not strong:
            suggs = suggestion_func(self.word, conf.rating_limit_hard, conf.rating_limit_hard_count)
            for suggestion in suggs:
                yield WordVariation(self, suggestion.word, variation_type)

        # Добавляем звездочку на конце
        if MatchTypes.MT_LAST_STAR in self.mt:
            yield WordVariation(self, f'{self.word}*', variation_type)

        # Добавляем слово "как есть", если это сокращение, то добавляем как частое слово
        if MatchTypes.MT_AS_IS in self.mt:
            yield WordVariation(
                self,
                self.bare_word if MatchTypes.MT_IS_SOCR else self.word,  # TODO: can be self.word
                VariationType.FREQ if MatchTypes.MT_IS_SOCR in self.mt else variation_type
            )

        # -- Дополнительные функции --
        # Добавляем сокращение
        if MatchTypes.MT_ADD_SOCR in self.mt and self.socr_word is not None:
            yield WordVariation(self, self.socr_word, VariationType.FREQ)

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
