# -*- coding: utf-8 -*-
from enum import Enum  # Типы вариаций слова


class VariationType(Enum):
    normal = 0
    freq = 1


class WordVariation:
    def __init__(self, parent_word, text, var_type=VariationType.normal):
        self.parent = parent_word
        self.text = text
        self.var_type = var_type
