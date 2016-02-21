# -*- coding: utf-8 -*-
import re
import time

import Levenshtein
import sphinxapi

from aore.config import basic
from aore.config import sphinx_conf
from aore.fias.wordentry import WordEntry
from aore.fias.wordvariation import VariationType
from aore.miscutils.trigram import trigram


class SphinxSearch:
    # Config's
    delta_len = 2

    default_rating_delta = 2
    regression_coef = 0.08
    max_result = 10

    # Конфиги, которые в будущем, возможно, будут настраиваемы пользователем (как strong)
    search_freq_words = True

    def __init__(self, db):
        self.db = db

        sphinx_host = sphinx_conf.listen
        sphinx_port = None
        if ":" in sphinx_conf.listen and "unix:/" not in sphinx_conf.listen:
            sphinx_host, sphinx_port = sphinx_conf.listen.split(":")
            sphinx_port = int(sphinx_port)

        self.client_sugg = sphinxapi.SphinxClient()
        self.client_sugg.SetServer(sphinx_host, sphinx_port)
        self.client_sugg.SetLimits(0, self.max_result)
        self.client_sugg.SetConnectTimeout(3.0)

        self.client_show = sphinxapi.SphinxClient()
        self.client_show.SetServer(sphinx_host, sphinx_port)
        self.client_show.SetLimits(0, self.max_result)
        self.client_show.SetConnectTimeout(3.0)

    def __configure(self, index_name, word_len):
        self.client_sugg.ResetFilters()
        if index_name == sphinx_conf.index_sugg:
            self.client_sugg.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
            self.client_sugg.SetFilterRange("len", int(word_len) - self.delta_len, int(word_len) + self.delta_len)
            self.client_sugg.SetSelect("word, len, @weight+{}-abs(len-{}) AS krank".format(self.delta_len, word_len))
            self.client_sugg.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")
        else:
            self.client_show.SetRankingMode(sphinxapi.SPH_RANK_BM25)
            self.client_show.SetSelect("aoid, fullname, @weight-2*abs(wordcount-{}) AS krank".format(word_len))
            self.client_show.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, "krank DESC")

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

    # Получает список объектов (слово)
    def __get_word_entries(self, words, strong):
        we_list = []
        for word in words:
            if word != '':
                we_list.append(WordEntry(self.db, word))

        return we_list

    def find(self, text, strong):
        def split_phrase(phrase):
            phrase = unicode(phrase).lower()
            return re.split(r"[ ,:.#$]+", phrase)

        # сплитим текст на слова
        words = split_phrase(text)

        # получаем список объектов (слов)
        word_entries = self.__get_word_entries(words, strong)
        word_count = len(word_entries)

        # проверяем, есть ли вообще что-либо в списке объектов слов (или же все убрали как частое)
        assert word_count > 0, "No legal words is specified"

        # получаем все вариации слов
        all_variations = []
        for we in word_entries:
            for vari in we.variations_gen(strong, self.__get_suggest):
                all_variations.append(vari)

        good_vars = [v for v in all_variations if v.var_type == VariationType.normal]
        freq_vars = [v for v in all_variations if v.var_type == VariationType.freq]

        good_vars_word_count = len(set([v.parent for v in good_vars]))
        freq_vars_word_count = len(set([v.parent for v in freq_vars]))

        # формируем строки для поиска в Сфинксе
        for i in range(good_vars_word_count, max(0, good_vars_word_count - 3), -1):
            first_q = "@fullname \"{}\"/{}".format(" ".join(good_var.text for good_var in good_vars), i)
            if self.search_freq_words and freq_vars_word_count:
                second_q = " @sname {}".format(" ".join(freq_var.text for freq_var in freq_vars))
                self.client_show.AddQuery(first_q + second_q, sphinx_conf.index_addjobj)
            self.client_show.AddQuery(first_q, sphinx_conf.index_addjobj)

            # if self.search_freq_words:
            #     for j in range(freq_vars_word_count, -1, -1):
            #         if j == 0:
            #             second_q = ""
            #         else:
            #             second_q = " @sname {}".format(" | ".join(freq_var.text for freq_var in freq_vars), j)
            #             second_q = second_q.replace("*", "")
            #
            #         print first_q + second_q
            #         self.client_show.AddQuery(first_q + second_q, sphinx_conf.index_addjobj)
            # else:
            #     print first_q
            #     self.client_show.AddQuery(first_q, sphinx_conf.index_addjobj)

        self.__configure(sphinx_conf.index_addjobj, word_count)

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
                        dict(aoid=ma['attrs']['aoid'], text=unicode(ma['attrs']['fullname']), ratio=ma['weight'],
                             cort=i))

        # results.sort(key=lambda x: Levenshtein.ratio(text, x['text']), reverse=False)

        return results
