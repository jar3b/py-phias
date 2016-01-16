# -*- coding: utf-8 -*-
import json
import re

import Levenshtein
import psycopg2
import aore.sphinxapi as sphinxapi

from aore.config import db as dbparams, sphinx_index_sugg, sphinx_index_addjobj
from aore.dbutils.dbimpl import DBImpl
from aore.fias.wordentry import WordEntry
from aore.miscutils.trigram import trigram


class SphinxSearch:
    def __init__(self):
        self.delta_len = 2
        self.rating_limit_soft = 0.4
        self.rating_limit_hard = 0.82
        self.default_rating_delta = 2
        self.regression_coef = 0.04

        self.db = DBImpl(psycopg2, dbparams)
        self.client = sphinxapi.SphinxClient()
        self.client.SetServer("localhost", 9312)
        self.client.SetLimits(0, 10)

        self.client1 = sphinxapi.SphinxClient()
        self.client1.SetServer("localhost", 9312)
        self.client1.SetLimits(0, 10)
        self.client1.SetConnectTimeout(7.0)

    def __configure(self, index_name, wlen=None):
        if index_name == "idx_fias_sugg":
            if wlen:
                self.client.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED2)
                self.client.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
                self.client.SetFilterRange("len", int(wlen) - self.delta_len, int(wlen) + self.delta_len)
                self.client.SetSelect("word, len, @weight+{}-abs(len-{}) AS krank".format(self.delta_len, wlen))
                self.client.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")

    def __get_suggest(self, word, rating_limit, count):
        word_len = str(len(word) / 2)
        trigrammed_word = '"{}"/1'.format(trigram(word))

        self.__configure(sphinx_index_sugg, word_len)
        result = self.client.Query(trigrammed_word, sphinx_index_sugg)

        # Если по данному слову не найдено подсказок (а такое бывает?)
        # возвращаем []
        if not result['matches']:
            return []

        maxrank = result['matches'][0]['attrs']['krank']
        maxleven = None

        outlist = list()
        for match in result['matches']:
            if len(outlist) >= count:
                break;

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

    def __add_word_variations(self, word_entry):
        if word_entry.MT_MANY_SUGG:
            suggs = self.__get_suggest(word_entry.word, self.rating_limit_soft, 6)
            for suggestion in suggs:
                word_entry.add_variation(suggestion[0])
        if word_entry.MT_SOME_SUGG:
            suggs = self.__get_suggest(word_entry.word, self.rating_limit_hard, 3)
            for suggestion in suggs:
                word_entry.add_variation(suggestion[0])
        if word_entry.MT_LAST_STAR:
            word_entry.add_variation(word_entry.word+'*')
        if word_entry.MT_AS_IS:
            word_entry.add_variation(word_entry.word)
        if word_entry.MT_ADD_SOCR:
            word_entry.add_variation_socr()


    def __get_word_entries(self, words):
        for word in words:
            if word != '':
                we = WordEntry(self.db, word)
                self.__add_word_variations(we)
                yield we


    def find(self, text):
        words = self.__split_phrase(text)
        word_entries = self.__get_word_entries(words)
        sentence = "{}".format(" MAYBE ".join(x.get_variations() for x in word_entries))
        #self.__configure(sphinx_index_addjobj)
        self.client1.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED2)
        self.client1.SetRankingMode(sphinxapi.SPH_RANK_SPH04)
        #self.client1.SetF
        rs = self.client1.Query(sentence, sphinx_index_addjobj)
        print rs
        for ma in rs['matches']:
            print ma['attrs']['fullname'], ma['weight']
        print sentence
