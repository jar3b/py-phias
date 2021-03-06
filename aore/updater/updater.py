import logging
import psycopg2
from os import walk, path

from aore.config import DatabaseConfig
from aore.dbutils.dbimpl import DBImpl
from aore.dbutils.dbschemas import allowed_tables, db_shemas
from aore.updater.aodataparser import AoDataParser
from aore.updater.aorar import AoRar
from aore.updater.aoxmltableentry import AoXmlTableEntry
from aore.updater.dbhandler import DbHandler


class Updater:
    # Source: "http", directory (as a full path to unpacked xmls)
    def __init__(self, source="http"):
        self.db_handler = DbHandler()
        self.source = source
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
        db = None
        try:
            db = DBImpl(psycopg2, DatabaseConfig)
            rows = db.get_rows('SELECT version FROM "CONFIG" WHERE id=0', True)
            assert len(rows) > 0, "Cannot get a version"
            return rows[0]['version']
        except:
            return 0
        finally:
            if db:
                db.close()

    @classmethod
    def __set__update_version(cls, updver=0):
        db = DBImpl(psycopg2, DatabaseConfig)
        try:
            assert isinstance(updver, int), "Update version must be of int type."
            db.execute('UPDATE "CONFIG" SET version={} WHERE id=0'.format(updver))
        finally:
            db.close()

    # Получает верию ФИАС с клавиатуры (если мы берем базу из папки или  локального архива и не можем определить,
    # что это за версия
    @staticmethod
    def __get_update_version_from_console():
        mode = None
        while not mode:
            try:
                mode = int(input('Enter FIAS update version (3 digit):'))
            except ValueError:
                print("Not a valid fias version, try again.")

        return mode

    def __get_updates_from_folder(self, foldername):
        fias_db_version = self.__get_update_version_from_console()
        yield dict(intver=fias_db_version,
                   textver="Version {}".format(fias_db_version),
                   delta_url=foldername,
                   complete_url=foldername)

    @staticmethod
    def __get_updates_from_rar(url):
        aorar = AoRar()

        if url.startswith("http://") or url.startswith("https://"):
            aorar.download(url)
        if url.endswith(".rar") and path.isfile(url):
            aorar.local(url)

        for table_entry in aorar.get_table_entries(allowed_tables):
            yield table_entry

    def __init_update_entries(self, updates_generator):
        if self.source == "http":
            assert updates_generator, "No generator"
            self.tablelist_generator = self.__get_updates_from_rar
            self.updalist_generator = updates_generator
            return
        if self.source.endswith(".rar"):
            self.tablelist_generator = self.__get_updates_from_rar
            self.updalist_generator = self.__get_updates_from_folder(self.source)
            return
        if path.isdir(self.source):
            self.tablelist_generator = self.__get_entries_from_folder
            self.updalist_generator = self.__get_updates_from_folder(self.source)

        assert self.tablelist_generator, "No valid source."

    def process_single_entry(self, operation_type, table_xmlentry, chunck_size=50000):
        aoparser = AoDataParser(table_xmlentry, chunck_size)
        aoparser.parse(lambda x, y: self.db_handler.bulk_csv(operation_type, table_xmlentry.table_name, x, y))

    def create(self, updates_generator):
        self.__init_update_entries(updates_generator)
        self.db_handler.create_structure()

        for update_entry in self.updalist_generator:
            logging.info("Processing DB #%d", update_entry['intver'])
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
            logging.info("Processing update #%d", update_entry['intver'])
            for table_entry in self.tablelist_generator(update_entry['delta_url']):
                self.process_single_entry(table_entry.operation_type, table_entry)
            Updater.__set__update_version(update_entry['intver'])
        else:
            logging.info("No updates more.")

        # Re-create all indexes (if dropped)
        if indexes_dropped:
            self.db_handler.create_indexes(allowed_tables)

        logging.info("Update success")
