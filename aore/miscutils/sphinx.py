# -*- coding: utf-8 -*-

import logging
import os

from bottle import template

from aore.aoutils.aoxmltableentry import AoXmlTableEntry
from aore.dbutils.dbhandler import DbHandler
from trigram import trigram

from aore.config import db as dbconfig, sphinx_index_addjobj, sphinx_var_dir, trashfolder, sphinx_index_sugg


class SphinxHelper:
    def __init__(self, ):
        self.index_binary = None
        self.files = dict()

    def configure_indexer(self, indexer_binary):
        logging.info("Start configuring Sphinx...")
        self.index_binary = indexer_binary

        # Create ADDROBJ config
        self.files['addrobj.conf'] = self.__create_ao_index_config()

        # Indexing ADDROBJ config
        run_index_cmd = "{} -c {} --all".format(self.index_binary, self.files['addrobj.conf'])
        logging.info("Indexing main ({})...".format(sphinx_index_addjobj))
        #os.system(run_index_cmd)
        logging.info("{} index was created.".format(sphinx_index_addjobj))

        # Produce dict file
        self.files['dict.txt'] = self.__create_suggestion_dict()

        # Put dict into db
        #self.files['dict.csv'] = self.__dbexport_sugg_dict()

        # Create SUGGEST config
        self.files['suggest.conf'] = self.__create_sugg_index_config()
        run_index_cmd = "{} -c {} --all".format(self.index_binary, self.files['suggest.conf'])
        logging.info("Indexing main ({})...".format(sphinx_index_sugg))
        os.system(run_index_cmd)
        logging.info("{} index was created.".format(sphinx_index_sugg))


    def __create_sugg_index_config(self):
        fname = os.path.abspath(trashfolder + "suggest.conf")
        logging.info("Creating config {}".format(fname))

        conf_data = template('aore/templates/sphinx/idx_suggest.conf', db_host=dbconfig['host'],
                             db_user=dbconfig['user'],
                             db_password=dbconfig['password'],
                             db_name=dbconfig['database'], db_port=dbconfig['port'],
                             index_name=sphinx_index_sugg,
                             sphinx_var_path=sphinx_var_dir)

        f = open(fname, "w")
        f.write(conf_data)
        f.close()

        logging.info("Done.")

        return fname

    def __dbexport_sugg_dict(self):
        logging.info("Place suggestion dict to DB {}...".format(self.files['dict.txt']))
        dict_dat_fname = os.path.abspath(trashfolder + "suggdict.csv")

        with open(self.files['dict.txt'], "r") as dict_file, open(dict_dat_fname, "w") as exit_file:
            line = None
            while line != '':
                nodes = []
                line = dict_file.readline()
                if line == '':
                    break

                keyword = line.split(' ')[0]
                if not keyword:
                    raise BaseException("Cannot process {}".format(self.files['dict.txt']))

                nodes.append(keyword)
                nodes.append(trigram(keyword))

                exit_file.write("\t".join(nodes) + "\n")

        aodp = DbHandler()
        aodp.bulk_csv(AoXmlTableEntry.OperationType.update, "AOTRIG", 8, dict_dat_fname)
        logging.info("Done.")

    def __create_ao_index_config(self):
        fname = os.path.abspath(trashfolder + "addrobj.conf")
        logging.info("Creating config {}".format(fname))

        conf_data = template('aore/templates/sphinx/idx_addrobj.conf', db_host=dbconfig['host'],
                             db_user=dbconfig['user'],
                             db_password=dbconfig['password'],
                             db_name=dbconfig['database'], db_port=dbconfig['port'],
                             sql_query=template('aore/templates/postgre/sphinx_query.sql').replace("\n", " \\\n"),
                             index_name=sphinx_index_addjobj,
                             sphinx_var_path=sphinx_var_dir)

        f = open(fname, "w")
        f.write(conf_data)
        f.close()

        logging.info("Done.")

        return fname

    def __create_suggestion_dict(self):
        fname = os.path.abspath(trashfolder + "suggdict.txt")
        logging.info("Make suggestion dict ({})...".format(fname))

        run_builddict_cmd = "{} {} -c {} --buildstops {} 200000 --buildfreqs".format(self.index_binary,
                                                                                     sphinx_index_addjobj,
                                                                                     self.files['addrobj.conf'], fname)
        #os.system(run_builddict_cmd)
        logging.info("Done.")

        return fname


# TRASH
#    conf_data = template('aore/templates/sphinx/sphinx.conf', sphinx_var_path=sphinx_var_dir)