from typing import TYPE_CHECKING, Tuple, List

if TYPE_CHECKING:
    from .wordentry import WordEntry


def _t(val: Tuple[str, float]) -> str:
    return val[0] if val[1] == 1 or val[0].endswith('*') else f'{val[0]}^{val[1]}'


class WordVariation:
    parent: 'WordEntry'
    full_words: List[Tuple[str, float]]
    abbr_words: List[Tuple[str, float]]

    def __init__(
            self,
            parent_word: 'WordEntry',
            full_words: List[Tuple[str, float]],
            abbr_words: List[Tuple[str, float]]
    ):
        self.parent = parent_word
        self.full_words = full_words
        self.abbr_words = abbr_words

    @property
    def has_short_words(self) -> bool:
        return len(self.abbr_words) > 0

    @property
    def is_empty(self) -> bool:
        return not self.full_words and not self.abbr_words

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, WordVariation) and hash(self) == hash(other)

    def __str__(self) -> str:
        return f'full={(", ".join([x[0] for x in self.full_words]))}, short={", ".join([x[0] for x in self.abbr_words])}'
