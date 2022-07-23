from enum import Enum
from typing import TYPE_CHECKING, Tuple, Dict

if TYPE_CHECKING:
    from .wordentry import WordEntry


class VariationType(int, Enum):
    """
    Типы вариаций слова
    """
    NORM = 0  # нормальный
    FREQ = 1  # частый


class WordVariation:
    parent: 'WordEntry'
    text: str
    var_type: VariationType
    extra_words: Tuple[Tuple[str, float], ...]

    def __init__(self, parent_word: 'WordEntry', text: str, var_type: VariationType = VariationType.NORM,
                 *extra_words: Tuple[str, float]):
        self.parent = parent_word
        self.text = text
        self.var_type = var_type
        self.extra_words = extra_words

    @property
    def search_text(self) -> str:
        if not self.extra_words:
            return self.text

        return '({})'.format(' | '.join([self.text, *[f'{x[0]}^{x[1]}' for x in self.extra_words]]))

    def __str__(self) -> str:
        return f'{self.search_text} ({self.var_type.name})'
