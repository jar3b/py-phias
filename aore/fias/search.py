# -*- coding: utf-8 -*-

import re

import Levenshtein
import psycopg2
import sphinxapi

from aore.config import db as dbparams
from aore.dbutils.dbimpl import DBImpl
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

    # Types =
    class SRankType:
        names = dict(
            SRANK_EXACTLY_MISSPRINT=['00'],  # Точно - опечатка, нужно много подсказок, без word*
            SRANK_EXACTLY_TYPING=['01', '11'],  # Точно - слово недопечатано, не надо подсказок, только word*
            SRANK_PROBABLY_TYPING=['0*'],  # Возможно - слово недопечатано, немного подсказок и word*
            SRANK_PROBABLY_FOUND=['10'],  # Возможно - слово введено точно, немного подсказок, без word*
            SRANK_PROBABLY_COMPLEX=['1*'],
            # Возможно, слово сложное, есть и точное совпадние, по маске Нужно немного подсказок и word*
            SRANK_PROBABLY_SOCR=['1!']  # Возможно - сокращение, не трогаем вообще
        )

        def __init__(self, rtype):
            self.rtype = rtype
            for x, y in self.names.iteritems():
                self.__dict__[x] = self.rtype in y

        def __str__(self):
            return ", ".join([x for x in self.names if self.__dict__[x]])

    def __get_strong_and_uncomplete_ranks(self, word):
        word_len = len(word)
        sql_qry = "SELECT COUNT(*) FROM \"AOTRIG\" WHERE word LIKE '{}%' AND LENGTH(word) > {} " \
                  "UNION ALL SELECT COUNT(*) FROM \"AOTRIG\" WHERE word='{}'".format(
            word, word_len, word)

        result = self.db.get_rows(sql_qry)
        strong_rank = result[1][0]
        uncomplete_rank = result[0][0]

        if uncomplete_rank > 1000 and word_len < 4:
            uncomplete_rank = '!'
        else:
            if uncomplete_rank > 1:
                uncomplete_rank = '*'

        return self.SRankType(str(strong_rank) + str(uncomplete_rank))

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

    def __process_word(self, word):
        print word, self.__get_strong_and_uncomplete_ranks(word)

    def find(self, text):
        words = self.__split_phrase(text)
        for word in words:
            self.__process_word(word)
            # result = self.client.Query(text)
            # print json.dumps(result)
            # logging.info("12")
