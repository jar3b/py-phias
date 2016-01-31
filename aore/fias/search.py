# -*- coding: utf-8 -*-
import logging
import re

import Levenshtein
import sphinxapi

from aore.config import sphinx_conf
from aore.fias.wordentry import WordEntry
from aore.miscutils.trigram import trigram


class SphinxSearch:
    def __init__(self, db):
        self.delta_len = 2

        self.rating_limit_soft = 0.4
        self.rating_limit_soft_count = 6
        self.word_length_soft = 3

        self.rating_limit_hard = 0.82
        self.rating_limit_hard_count = 3

        self.default_rating_delta = 2
        self.regression_coef = 0.04

        self.db = db
        self.client_sugg = sphinxapi.SphinxClient()
        self.client_sugg.SetServer(sphinx_conf.host_name, sphinx_conf.port)
        self.client_sugg.SetLimits(0, 10)
        self.client_sugg.SetConnectTimeout(3.0)

        self.client_show = sphinxapi.SphinxClient()
        self.client_show.SetServer(sphinx_conf.host_name, sphinx_conf.port)
        self.client_show.SetLimits(0, 10)
        self.client_show.SetConnectTimeout(3.0)

    def __configure(self, index_name, wlen=None):
        if index_name == sphinx_conf.index_sugg:
            if wlen:
                self.client_sugg.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED2)
                self.client_sugg.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
                self.client_sugg.SetFilterRange("len", int(wlen) - self.delta_len, int(wlen) + self.delta_len)
                self.client_sugg.SetSelect("word, len, @weight+{}-abs(len-{}) AS krank".format(self.delta_len, wlen))
                self.client_sugg.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")
        else:
            self.client_show.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED2)
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

        outlist.sort(key=lambda x: x[1], reverse=True)

        return outlist

    def __split_phrase(self, phrase):
        phrase = unicode(phrase).replace('-', '').replace('@', '').lower()
        return re.split(r"[ ,:.#$]+", phrase)

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

    def __get_word_entries(self, words, strong):
        for word in words:
            if not strong and len(word) < self.word_length_soft:
                continue
            if word != '':
                we = WordEntry(self.db, word)
                self.__add_word_variations(we, strong)

                if we.get_variations() == "()":
                    raise BaseException("Cannot process sentence.")
                yield we

    def find(self, text, strong):
        words = self.__split_phrase(text)
        word_entries = self.__get_word_entries(words, strong)
        sentence = "{}".format(" MAYBE ".join(x.get_variations() for x in word_entries))

        self.__configure(sphinx_conf.index_addjobj)
        logging.info("QUERY " + sentence)
        rs = self.client_show.Query(sentence, sphinx_conf.index_addjobj)
        logging.info("OK")

        results = []
        for ma in rs['matches']:
            results.append(dict(aoid=ma['attrs']['aoid'], text=ma['attrs']['fullname'], ratio=ma['weight']))

        if strong:
            results.sort(key=lambda x: Levenshtein.ratio(text, x['text']), reverse=True)

        return results
