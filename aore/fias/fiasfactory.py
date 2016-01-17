# -*- coding: utf-8 -*-
from aore.fias.search import SphinxSearch


class FiasFactory:
    def __init__(self):
        self.searcher = SphinxSearch()

    # text - строка поиска
    # strong - строгий поиск или "мягкий" (с допущением ошибок, опечаток)
    # out_format - "full" or "simple" - полный (подробно для каждого подпункта) или простой (только строка и AOID)
    def find(self, text, strong=False, out_format="simple"):
        try:
            results = self.searcher.find(text, strong)

        except:
            return []
