from enum import Enum
from typing import TYPE_CHECKING

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

    def __init__(self, parent_word: 'WordEntry', text: str, var_type: VariationType = VariationType.NORM):
        self.parent = parent_word
        self.text = text
        self.var_type = var_type
