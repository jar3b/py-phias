from typing import List, Tuple

from .wordvariation import WordVariation


def _t(val: Tuple[str, float]) -> str:
    return val[0] if val[1] == 1 else f'{val[0]}^{val[1]}'


class SearchQueryGenerator:
    __slots__ = ['full_words_list', 'short_words_list', 'strip_word_list']
    full_words_list: List[str]
    short_words_list: List[str]
    strip_word_list: List[str]

    def __init__(self, variations: List[WordVariation]):
        full_words_list = []
        short_words_list = []
        strip_word_list = []

        for v in variations:
            if v.has_short_words:
                short_words_list.append(' '.join([x[0] for x in v.abbr_words]))
            else:
                strip_word_list.append(self.__get_word_text([_t(x) for x in v.full_words]))

            full_words_list.append(self.__get_word_text([_t(x) for x in v.full_words]))

        self.full_words_list = [x for x in full_words_list if x]
        self.short_words_list = [x for x in short_words_list if x]
        self.strip_word_list = [x for x in strip_word_list if x]

    @staticmethod
    def __get_word_text(words: List[str]) -> str | None:
        if not words:
            return None
        if len(words) == 1:
            return words[0]
        return "({})".format(" | ".join(words))

    def get_query(self, op: str = ' ', with_short: bool = False) -> str:
        if not op.startswith(' '):
            op = ' ' + op
        if not op.endswith(' '):
            op = op + ' '

        main_list = self.strip_word_list if with_short else self.full_words_list

        result = '@fullname {}'.format(op.join(main_list))
        if with_short and self.short_words_list:
            result += ' @sname {}'.format(' '.join(self.short_words_list))
        return result
