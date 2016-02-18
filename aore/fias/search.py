# -*- coding: utf-8 -*-
import re

import Levenshtein
import sphinxapi
import time

from aore.config import sphinx_conf
from aore.fias.wordentry import WordEntry
from aore.miscutils.trigram import trigram
from aore.config import basic


class SphinxSearch:
    # Config's
    delta_len = 2

    rating_limit_soft = 0.41
    rating_limit_soft_count = 6

    rating_limit_hard = 0.82
    rating_limit_hard_count = 3

    default_rating_delta = 2
    regression_coef = 0.08
    max_result = 10

    exclude_freq_words = True

    def __init__(self, db):
        self.db = db
        self.client_sugg = sphinxapi.SphinxClient()
        self.client_sugg.SetServer(sphinx_conf.host_name, sphinx_conf.port)
        self.client_sugg.SetLimits(0, self.max_result)
        self.client_sugg.SetConnectTimeout(3.0)

        self.client_show = sphinxapi.SphinxClient()
        self.client_show.SetServer(sphinx_conf.host_name, sphinx_conf.port)
        self.client_show.SetLimits(0, self.max_result)
        self.client_show.SetConnectTimeout(3.0)

    def __configure(self, index_name, wlen=None):
        self.client_sugg.ResetFilters()
        if index_name == sphinx_conf.index_sugg and wlen:
            self.client_sugg.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
            self.client_sugg.SetFilterRange("len", int(wlen) - self.delta_len, int(wlen) + self.delta_len)
            self.client_sugg.SetSelect("word, len, @weight+{}-abs(len-{}) AS krank".format(self.delta_len, wlen))
            self.client_sugg.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")
        else:
            self.client_show.SetRankingMode(sphinxapi.SPH_RANK_BM25)
            self.client_show.SetSortMode(sphinxapi.SPH_SORT_RELEVANCE)

    def __get_suggest(self, word, rating_limit, count):
        word_len = str(len(word) / 2)
        trigrammed_word = '"{}"/1'.format(trigram(word))

        self.__configure(sphinx_conf.index_sugg, word_len)
        result = self.client_sugg.Query(trigrammed_word, sphinx_conf.index_sugg)

        # Если по данному слову не найдено подсказок (а такое бывает?)
        # возвращаем []

        if not result['matches']:
            return []

        maxrank = result['matches'][0]['attrs']['krank']
        maxleven = None

        outlist = list()
        for match in result['matches']:
            if len(outlist) >= count:
                break

            if maxrank - match['attrs']['krank'] < self.default_rating_delta:
                jaro_rating = Levenshtein.jaro(word, match['attrs']['word'])
                if not maxleven:
                    maxleven = jaro_rating - jaro_rating * self.regression_coef
                if jaro_rating >= rating_limit and jaro_rating >= maxleven:
                    outlist.append([match['attrs']['word'], jaro_rating])
                del jaro_rating

        outlist.sort(key=lambda x: x[1], reverse=True)

        return outlist

    def __add_word_variations(self, word_entry, strong):
        if word_entry.MT_MANY_SUGG and not strong:
            suggs = self.__get_suggest(word_entry.word, self.rating_limit_soft, self.rating_limit_soft_count)
            for suggestion in suggs:
                word_entry.add_variation(suggestion[0])
        if word_entry.MT_SOME_SUGG and not strong:
            suggs = self.__get_suggest(word_entry.word, self.rating_limit_hard, self.rating_limit_hard_count)
            for suggestion in suggs:
                word_entry.add_variation(suggestion[0])
        if word_entry.MT_LAST_STAR:
            word_entry.add_variation(word_entry.word + '*')
        if word_entry.MT_AS_IS:
            word_entry.add_variation(word_entry.word)
        if word_entry.MT_ADD_SOCR:
            word_entry.add_variation_socr()

    # Получает список объектов (слово), пропуская часто используемые слова
    def __get_word_entries(self, words, strong):
        we_list = []
        for word in words:
            if word != '':
                we = WordEntry(self.db, word)
                if self.exclude_freq_words and we.is_freq_word:
                    pass
                else:
                    self.__add_word_variations(we, strong)

                    assert we.get_variations() != "", "Cannot process sentence."
                    we_list.append(we)

        return we_list

    def find(self, text, strong):
        def split_phrase(phrase):
            phrase = unicode(phrase).replace('-', '').replace('@', '').lower()
            return re.split(r"[ ,:.#$]+", phrase)

        # сплитим текст на слова
        words = split_phrase(text)

        # получаем список объектов
        word_entries = self.__get_word_entries(words, strong)
        word_count = len(word_entries)

        # проверяем, есть ли вообще что-либо в списке объектов слов (или же все убрали как частое)
        assert word_count > 0, "No legal words is specified"

        # формируем строки для поиска в Сфинксе
        for x in range(word_count, max(0, word_count - 3), -1):
            self.client_show.AddQuery("\"{}\"/{}".format(" ".join(x.get_variations() for x in word_entries), x),
                                      sphinx_conf.index_addjobj)

        self.__configure(sphinx_conf.index_addjobj)

        start_t = time.time()
        rs = self.client_show.RunQueries()
        elapsed_t = time.time() - start_t

        if basic.logging:
            print(elapsed_t)

        results = []
        parsed_ids = []

        for i in range(0, len(rs)):
            for ma in rs[i]['matches']:
                if len(results) >= self.max_result:
                    break
                if not ma['attrs']['aoid'] in parsed_ids:
                    parsed_ids.append(ma['attrs']['aoid'])
                    results.append(
                        dict(aoid=ma['attrs']['aoid'], text=unicode(ma['attrs']['fullname']), ratio=ma['weight'], cort=i))

        results.sort(key=lambda x: Levenshtein.ratio(text, x['text']), reverse=True)

        return results
