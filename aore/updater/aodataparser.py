# -*- coding: utf-8 -*-
import os
import codecs
from aore.config import Folders
from aore.dbutils.dbschemas import db_shemas
from aore.miscutils.exceptions import FiasException
from aore.updater.xmlparser import XMLParser


class AoDataParser:
    def __init__(self, datasource, pagesize):
        self.datasource = datasource
        if self.datasource.table_name not in db_shemas:
            raise FiasException("Cannot parse {}: Not configured.".format(self.datasource.table_name))
        else:
            self.allowed_fields = db_shemas[self.datasource.table_name].fields

        # Создаем временную папку, если ее нет
        if not os.path.exists(Folders.temp):
            os.makedirs(Folders.temp)

        self.pagesize = pagesize
        self.currentpage = 0
        self.counter = 0

        self.base_filename = ""
        self.csv_file = None
        self.data_bereit_callback = None

    def import_update(self, attr):
        if self.counter > self.pagesize:
            # Send old file to DB engine
            if self.csv_file:
                self.csv_file.close()
                self.data_bereit_callback(self.counter, os.path.abspath(self.csv_file.name))
                os.remove(self.csv_file.name)

            # Prepare to next iteration
            self.counter = 0
            self.currentpage += 1
            self.csv_file = codecs.open(self.base_filename.format(self.currentpage), "w", "utf-8")

        exit_nodes = list()
        for allowed_field in self.allowed_fields:
            if allowed_field in attr:
                exit_nodes.append(attr[allowed_field])
            else:
                exit_nodes.append("NULL")

        exit_string = "\t".join(exit_nodes)
        self.csv_file.write(exit_string + "\n")
        self.counter += 1

    # Output - sql query
    def parse(self, data_callback):
        self.data_bereit_callback = data_callback
        self.currentpage = 0
        self.base_filename = \
            Folders.temp + "/fd_" + \
            str(self.datasource.operation_type) + "_" + \
            self.datasource.table_name + ".csv.part{}"
        self.counter = self.pagesize + 1

        xml_parser = XMLParser(self.import_update)
        src = self.datasource.open()
        xml_parser.parse_buffer(src, db_shemas[self.datasource.table_name].xml_tag)

        # Send last file to db processor
        if self.csv_file:
            self.csv_file.close()
            self.data_bereit_callback(self.counter, os.path.abspath(self.csv_file.name))
            os.remove(self.csv_file.name)
        src.close()
