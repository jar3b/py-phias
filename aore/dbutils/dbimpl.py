# -*- coding: utf-8 -*-

from traceback import format_exc


class DBImpl:
    def __init__(self, engine, params):
        self.db_engine = engine
        self.connection = engine.connect(**params)

    def transaction_commit(self):
        self.connection.commit()

    def transaction_rollback(self):
        self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()

    def get_cursor(self):
        return self.connection.cursor()

    def execute(self, sql_query):
        try:
            cur = self.get_cursor()
            cur.execute(sql_query)
            self.transaction_commit()
        except:
            self.transaction_rollback()
            raise BaseException("Error execute sql query. Reason : {}".format(format_exc()))

    def get_rows(self, query_string, for_dict=True):
        if for_dict:
            cur = self.connection.cursor(self.db_engine.cursors.DictCursor)
        else:
            cur = self.connection.cursor()
        cur.execute(query_string)

        rows = cur.fetchall()
        if cur:
            cur.close()

        return rows
