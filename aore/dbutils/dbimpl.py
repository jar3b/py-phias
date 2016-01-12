# -*- coding: utf-8 -*-


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