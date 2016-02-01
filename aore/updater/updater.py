# -*- coding: utf-8 -*-

import logging
from os import walk, path

from aore.config import db_conf
from aore.dbutils.dbimpl import DBImpl
from aore.dbutils.dbschemas import allowed_tables, db_shemas
from aore.updater.aodataparser import AoDataParser
from aore.updater.aorar import AoRar
from aore.updater.aoxmltableentry import AoXmlTableEntry
from aore.updater.dbhandler import DbHandler
import psycopg2


class Updater:
    # Source: "http", directory (as a full path to unpacked xmls)
    def __init__(self, source="http"):
        self.db_handler = DbHandler()
        self.mode = source
        self.updalist_generator = None
        self.tablelist_generator = None
        self.allowed_tables = None

    def __get_entries_from_folder(self, path_to_xmls):
        for (dirpath, dirnames, filenames) in walk(path_to_xmls):
            for filename in filenames:
                if filename.endswith(".XML"):
                    xmltable = AoXmlTableEntry.from_dir(filename, dirpath.replace("\\", "/") + "/")
                    if xmltable.table_name in allowed_tables:
                        yield xmltable
            break

    @classmethod
    def get_current_fias_version(cls):
        db = DBImpl(psycopg2, db_conf)
        try:
            rows = db.get_rows('SELECT version FROM "CONFIG" WHERE id=0', True)
            assert len(rows) > 0, "Cannot get a version"
            return rows[0]['version']
        finally:
            db.close()

    @classmethod
    def __set__update_version(cls, updver = 0):
        db = DBImpl(psycopg2, db_conf)
        try:
            assert type(updver) is int, "Update version must be of int type."
            db.execute('UPDATE "CONFIG" SET version={} WHERE id=0'.format(updver))
        finally:
            db.close()


    def __get_updates_from_folder(self, foldername):
        # TODO: Вычислять версию, если берем данные из каталога
        yield dict(intver=0, textver="Unknown", delta_url=foldername, complete_url=foldername)

    def __get_updates_from_rar(self, url):
        aorar = AoRar()
        fname = aorar.download(url)
        for table_entry in aorar.get_table_entries(fname, allowed_tables):
            yield table_entry

    def __init_update_entries(self, updates_generator):
        if self.mode == "http":
            assert updates_generator
            self.tablelist_generator = self.__get_updates_from_rar
            self.updalist_generator = updates_generator
        else:
            assert path.isdir(self.mode), "Invalid directory {}".format(self.mode)
            self.updalist_generator = self.__get_updates_from_folder(self.mode)
            self.tablelist_generator = self.__get_entries_from_folder

    def process_single_entry(self, operation_type, table_xmlentry, chunck_size=50000):
        aoparser = AoDataParser(table_xmlentry, chunck_size)
        aoparser.parse(lambda x, y: self.db_handler.bulk_csv(operation_type, table_xmlentry.table_name, x, y))

    def create(self, updates_generator):
        self.__init_update_entries(updates_generator)
        self.db_handler.create_structure()

        for update_entry in self.updalist_generator:
            logging.info("Processing DB #{}".format(update_entry['intver']))
            for table_entry in self.tablelist_generator(update_entry['complete_url']):
                if table_entry.operation_type == AoXmlTableEntry.OperationType.update:
                    table_entry.operation_type = AoXmlTableEntry.OperationType.create
                self.process_single_entry(table_entry.operation_type, table_entry)
            Updater.__set__update_version(update_entry['intver'])
        else:
            logging.info("No updates more.")

        self.db_handler.create_indexes(db_shemas.keys())

        logging.info("Create success")

    def update(self, updates_generator):
        self.__init_update_entries(updates_generator)

        # Drop all indexes if updates needed
        indexes_dropped = False

        for update_entry in self.updalist_generator:
            if not indexes_dropped:
                self.db_handler.drop_indexes(allowed_tables)
                indexes_dropped = True
            logging.info("Processing update #{}".format(update_entry['intver']))
            for table_entry in self.tablelist_generator(update_entry['delta_url']):
                self.process_single_entry(table_entry.operation_type, table_entry)
            Updater.__set__update_version(update_entry['intver'])
        else:
            logging.info("No updates more.")

        # Re-create all indexes (if dropped)
        if indexes_dropped:
            self.db_handler.create_indexes(allowed_tables)

        logging.info("Update success")
