# -*- coding: utf-8 -*-

import logging

import psycopg2
from bottle import template

from aore.config import db_conf
from aore.dbutils.dbimpl import DBImpl
from aore.dbutils.dbschemas import db_shemas
from aore.updater.aoxmltableentry import AoXmlTableEntry


class DbHandler:
    def __init__(self):
        self.db = DBImpl(psycopg2, db_conf)

    def bulk_csv(self, operation_type, table_name, processed_count, csv_file_name):
        sql_query = None

        # simple add new reocrds
        if operation_type == AoXmlTableEntry.OperationType.create:
            sql_query = template('aore/templates/postgre/bulk_create.sql', delim='\t', tablename=table_name,
                                 fieldslist=", ".join(db_shemas[table_name].fields), csvname=csv_file_name)

        # update table
        if operation_type == AoXmlTableEntry.OperationType.update:
            fields_update_list = ""
            for field in db_shemas[table_name].fields:
                if field != db_shemas[table_name].unique_field.upper():
                    fields_update_list += "{}=EXCLUDED.{}, ".format(field, field)
            fields_update_list = fields_update_list[:-2]

            sql_query = template('aore/templates/postgre/bulk_update.sql', delim='\t', tablename=table_name,
                                 fieldslist=", ".join(db_shemas[table_name].fields), csvname=csv_file_name,
                                 uniquekey=db_shemas[table_name].unique_field, updaterule=fields_update_list)

        # delete records from table
        if operation_type == AoXmlTableEntry.OperationType.delete:
            sql_query = template('aore/templates/postgre/bulk_delete.sql', delim='\t', tablename=table_name,
                                 fieldslist=", ".join(db_shemas[table_name].fields), csvname=csv_file_name,
                                 uniquekey=db_shemas[table_name].unique_field)

        assert sql_query, "Invalid operation type: {}".format(operation_type)

        self.db.execute(sql_query)
        logging.info("Processed {} queries FROM {}".format(processed_count - 1, csv_file_name))

    def pre_create(self):
        logging.info("Prepare to create DB structure...")
        sql_query = template("aore/templates/postgre/pre_create.sql")

        self.db.execute(sql_query)

    def post_create(self):
        logging.info("Indexing ADDROBJ...")
        sql_query = template("aore/templates/postgre/post_create.sql")

        self.db.execute(sql_query)
        logging.info("Indexing done.")

    def pre_update(self):
        # TODO: update actions
        pass
