# -*- coding: utf-8 -*-

from aore.aoutils.aodataparser import AoDataParser
from aore.config import db as dbparams
from aore.aoutils.aorar import AoRar
from aore.aoutils.aoxmltableentry import AoXmlTableEntry
from aore.dbutils.dbschemas import db_shemas, allowed_tables
from aore.aoutils.importer import Importer
from os import walk
from traceback import format_exc
import psycopg2
import logging
from aore.dbutils.dbimpl import DBImpl


class AoUpdater:
    def __init__(self, dirpath=None):
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.dirpath = None
        self.updatelist = None
        self.db = DBImpl(psycopg2, dbparams)

        if dir:
            self.dirpath = dirpath
        else:
            imp = Importer()
            self.updatelist = imp.download_updatelist

    def get_table_entries(self, allowed_tables):
        for (dirpath, dirnames, filenames) in walk(self.dirpath):
            for filename in filenames:
                if filename.endswith(".XML"):
                    xmltable = AoXmlTableEntry.from_dir(filename, dirpath.replace("\\", "/") + "/")
                    if xmltable.table_name in allowed_tables:
                        yield xmltable
            break

    def on_receive_sql_file(self, chunck_size, table_name, csv_file_name):
        sql_query = "COPY \"{}\" ({}) FROM '{}' DELIMITER '\t' NULL 'NULL'".format(table_name,
                                                                       ", ".join(db_shemas[table_name].fields),
                                                                       csv_file_name)
        print sql_query
        try:
            cur = self.db.get_cursor()
            cur.execute(sql_query)
            self.db.transaction_commit()
        except:
            self.db.transaction_rollback()
            logging.error("Error updating sql. Reason : {}".format(format_exc()))

        logging.warning("Inserted {} queries FROM {}".format(chunck_size, csv_file_name))

    def update_one_delta(self, table_xmlentry, chunck_size=50000):
        aoparser = AoDataParser(table_xmlentry, chunck_size)
        aoparser.parse(lambda x: self.on_receive_sql_file(chunck_size, table_xmlentry.table_name, x))

    def __pre_create_db(self):
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

    def create(self):
        if not self.dirpath:
            logging.warning("Cannot update - Updater works in update mode")
            return
        self.__pre_create_db()

        for table_entry in self.get_table_entries(allowed_tables):
            self.update_one_delta(table_entry)

    def update(self, count=1):
        if not self.updatelist:
            logging.warning("Cannot update - Updater works in dir mode")
            return

        counter = 0
        for fias_update in self.updatelist:
            counter += 1
            if counter > count:
                return

            aorar = AoRar()
            fname = aorar.download(fias_update['url'])
            for table_entry in aorar.get_table_entries(fname, allowed_tables):
                self.update_one_delta(table_entry)
