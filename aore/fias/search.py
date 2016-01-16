# -*- coding: utf-8 -*-

import re

import Levenshtein
import psycopg2
import sphinxapi

from aore.config import db as dbparams
from aore.dbutils.dbimpl import DBImpl
from aore.fias.word import WordEntry
from aore.miscutils.trigram import trigram


class SphinxSearch:
    def __init__(self):
        self.delta_len = 2
        self.db = DBImpl(psycopg2, dbparams)
        self.client = sphinxapi.SphinxClient()
        self.client.SetServer("localhost", 9312)
        self.client.SetLimits(0, 10)

    def __configure(self, index_name, wlen=None):
        if index_name == "idx_fias_sugg":
            if wlen:
                self.client.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED2)
                self.client.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
                self.client.SetFilterRange("len", int(wlen) - self.delta_len, int(wlen) + self.delta_len)
                self.client.SetSelect("word, len, @weight+{}-abs(len-{}) AS krank".format(self.delta_len, wlen))
                self.client.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")
            else:
                self.client.SetMatchMode(sphinxapi.MA)

    def __get_suggest(self, word):
        word_len = str(len(word) / 2)
        trigrammed_word = '"{}"/1'.format(trigram(word))

        self.__configure("idx_fias_sugg", word_len)
        result = self.client.Query(trigrammed_word, 'idx_fias_sugg')

        # Если по данному слову не найдено подсказок (а такое бывает?)
        # возвращаем []
        if not result['matches']:
            return []

        maxrank = result['matches'][0]['attrs']['krank']
        outlist = list()
        for match in result['matches']:
            if maxrank - match['attrs']['krank'] < 2:
                outlist.append([match['attrs']['word'], Levenshtein.jaro(word, match['attrs']['word'])])
        outlist.sort(key=lambda x: x[1], reverse=True)

        for x in outlist:
            print x[0], x[1]
        return outlist

    def __split_phrase(self, phrase):
        phrase = unicode(phrase).replace('-', '').replace('@', '').lower()
        return re.split(r"[ ,:.]+", phrase)

    def __process_words(self, words):
        for word in words:
            yield WordEntry(self.db, word)

    def find(self, text):
        words = self.__split_phrase(text)
        word_entries = self.__process_words(words)
        for word_entry in word_entries:
            print word_entry, word_entry.get_type()
            # result = self.client.Query(text)
            # print json.dumps(result)
            # logging.info("12")
