# -*- coding: utf-8 -*-

import logging
from traceback import format_exc

import psycopg2

from aore.config import db as dbparams
from aore.dbutils.dbimpl import DBImpl
from aore.dbutils.dbschemas import db_shemas


class DbHandler:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.db = DBImpl(psycopg2, dbparams)

    def bulk_csv(self, chunk_size, table_name, csv_file_name):
        sql_query = "COPY \"{}\" ({}) FROM '{}' DELIMITER '\t' NULL 'NULL'". \
            format(table_name,
                   ", ".join(
                       db_shemas[table_name].fields),
                   csv_file_name)
        try:
            cur = self.db.get_cursor()
            cur.execute(sql_query)
            self.db.transaction_commit()
        except:
            self.db.transaction_rollback()
            raise BaseException("Error updating sql. Reason : {}".format(format_exc()))

        logging.warning("Inserted {} queries FROM {}".format(chunk_size, csv_file_name))

    def pre_create(self):
        f = open("aore/templates/postgre/pre_create.sql")
        create_db_syntax = f.read()
        f.close()

        try:
            cur = self.db.get_cursor()
            cur.execute(create_db_syntax)
            self.db.transaction_commit()
        except:
            self.db.transaction_rollback()
            raise "Error downloading. Reason : {}".format(format_exc())

    def pre_update(self):
        # TODO: update actions
        pass
