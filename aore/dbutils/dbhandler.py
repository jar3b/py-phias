# -*- coding: utf-8 -*-

import logging

import psycopg2

from aore.aoutils.aoxmltableentry import AoXmlTableEntry
from aore.config import db as dbparams
from aore.dbutils.dbimpl import DBImpl
from aore.dbutils.dbschemas import db_shemas


class DbHandler:
    def __init__(self):
        self.db = DBImpl(psycopg2, dbparams)

        f = open("aore/templates/postgre/bulk_create.sql")
        self.syntax_bulk_create = f.read()
        f.close()

        f = open("aore/templates/postgre/bulk_update.sql")
        self.syntax_bulk_update = f.read()
        f.close()

        f = open("aore/templates/postgre/bulk_delete.sql")
        self.syntax_bulk_delete = f.read()
        f.close()

    def bulk_csv(self, operation_type, table_name, processed_count, csv_file_name):
        sql_query = None

        # simple add new reocrds
        if operation_type == AoXmlTableEntry.OperationType.create:
            sql_query = self.syntax_bulk_create \
                .replace("%tab%", "\t") \
                .replace("%tablename%", table_name) \
                .replace("%fieldslist%", ", ".join(db_shemas[table_name].fields)) \
                .replace("%csvname%", csv_file_name)

        # update table
        if operation_type == AoXmlTableEntry.OperationType.update:
            fields_update_list = ""
            for field in db_shemas[table_name].fields:
                if field != db_shemas[table_name].unique_field.upper():
                    fields_update_list += "{}=EXCLUDED.{}, ".format(field, field)
            fields_update_list = fields_update_list[:-2]

            sql_query = self.syntax_bulk_update \
                .replace("%tab%", "\t") \
                .replace("%tablename%", table_name) \
                .replace("%fieldslist%", ", ".join(db_shemas[table_name].fields)) \
                .replace("%csvname%", csv_file_name) \
                .replace("%uniquekey%", db_shemas[table_name].unique_field) \
                .replace("%updaterule%", fields_update_list)

            if table_name == "ADDROBJ":
                sql_query += "DELETE FROM \"%tablename%\" WHERE %filterrule%;" \
                    .replace("%tablename%", table_name) \
                    .replace("%filterrule%",
                             "ACTSTATUS = FALSE OR NEXTID IS NOT NULL")

        # delete records from table
        if operation_type == AoXmlTableEntry.OperationType.delete:
            sql_query = self.syntax_bulk_delete \
                .replace("%tab%", "\t") \
                .replace("%tablename%", table_name) \
                .replace("%fieldslist%", ", ".join(db_shemas[table_name].fields)) \
                .replace("%csvname%", csv_file_name) \
                .replace("%uniquekey%", db_shemas[table_name].unique_field)

        assert sql_query, "Invalid operation type: {}".format(operation_type)

        self.db.execute(sql_query)
        logging.info("Processed {} queries FROM {}".format(processed_count-1, csv_file_name))

    def pre_create(self):
        f = open("aore/templates/postgre/pre_create.sql")
        sql_query = f.read()
        f.close()

        self.db.execute(sql_query)

    def pre_update(self):
        # TODO: update actions
        pass
