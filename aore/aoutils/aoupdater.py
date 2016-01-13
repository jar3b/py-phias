# -*- coding: utf-8 -*-

import logging
from os import walk, path

from aore.aoutils.aodataparser import AoDataParser
from aore.aoutils.aorar import AoRar
from aore.aoutils.aoxmltableentry import AoXmlTableEntry
from aore.aoutils.importer import Importer
from aore.dbutils.dbhandler import DbHandler
from aore.dbutils.dbschemas import allowed_tables


class AoUpdater:
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

    def __get_updates_from_folder(self, foldername):
        # TODO: Вычислять версию, если берем данные из каталога
        yield dict(intver=0, textver="Unknown", url=foldername)

    def __get_updates_from_rar(self, url):
        aorar = AoRar()
        fname = aorar.download(url)
        for table_entry in aorar.get_table_entries(fname, allowed_tables):
            yield table_entry

    def __init_update_entries(self, full_base):
        if self.mode == "http":
            self.tablelist_generator = self.__get_updates_from_rar
            imp = Importer()
            if full_base:
                self.updalist_generator = imp.get_full()
            else:
                self.updalist_generator = imp.get_updates()
        else:
            assert path.isdir(self.mode), "Invalid directory {}".format(self.mode)
            self.updalist_generator = self.__get_updates_from_folder(self.mode)
            self.tablelist_generator = self.__get_entries_from_folder

    def process_single_entry(self, operation_type, table_xmlentry, chunck_size=50000):
        aoparser = AoDataParser(table_xmlentry, chunck_size)
        aoparser.parse(lambda x, y: self.db_handler.bulk_csv(operation_type, table_xmlentry.table_name, x, y))

    def create(self):
        self.__init_update_entries(True)
        self.db_handler.pre_create()

        for update_entry in self.updalist_generator:
            for table_entry in self.tablelist_generator(update_entry['url']):
                if table_entry.operation_type == AoXmlTableEntry.OperationType.update:
                    table_entry.operation_type = AoXmlTableEntry.OperationType.create
                self.process_single_entry(table_entry.operation_type, table_entry)

        self.db_handler.post_create()

        logging.info("Create success")

    def update(self, count=1):
        self.__init_update_entries(False)
        self.db_handler.pre_update()

        counter = 0
        for update_entry in self.updalist_generator:
            counter += 1
            if counter > count:
                logging.warning("Maximum count of updates ({}) are processed - exit".format(count))
                break

            for table_entry in self.tablelist_generator(update_entry['url']):
                self.process_single_entry(table_entry.operation_type, table_entry)

        logging.info("Update success")
