# -*- coding: utf-8 -*-

from traceback import format_exc
import psycopg2.extras


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

    def get_rows(self, query_string, dict_cursor=False):
        if dict_cursor:
            cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cur = self.connection.cursor()
        cur.execute(query_string)

        rows = cur.fetchall()
        if cur:
            cur.close()

        return rows
