# -*- coding: utf-8 -*-

import logging
import os

from bottle import template

from aore.config import folders, db_conf, sphinx_conf
from aore.miscutils.trigram import trigram
from aore.updater.aoxmltableentry import AoXmlTableEntry
from aore.updater.dbhandler import DbHandler


class SphinxHelper:
    def __init__(self):
        self.index_binary = None
        self.files = dict()
        self.aodp = DbHandler()

        # Создаем временную папку, если ее нет
        if not os.path.exists(folders.temp):
            os.makedirs(folders.temp)

    def configure_indexer(self, indexer_binary, config_filename):
        logging.info("Start configuring Sphinx...")
        self.index_binary = indexer_binary

        # Create ADDROBJ config
        self.files['addrobj.conf'] = self.__create_ao_index_config()

        # Produce dict file
        self.files['dict.txt'] = self.__create_suggestion_dict()

        # Put dict into db
        self.files['dict.csv'] = self.__dbexport_sugg_dict()

        # Create SUGGEST config
        self.files['suggest.conf'] = self.__create_sugg_index_config()

        # Create main config (sphinx.conf)
        out_fname = self.__create_main_config(config_filename)

        # Indexing both configs
        run_index_cmd = "{} -c {} --all --rotate".format(self.index_binary, out_fname)
        logging.info("Indexing main (%s)...", out_fname)
        os.system(run_index_cmd)
        logging.info("All indexes were created.")

        # remove temp files
        for fname, fpath in self.files.iteritems():
            try:
                os.remove(fpath)
            except:
                logging.warning("Cannot delete %s. Not accessible.", fpath)
        logging.info("Temporary files removed.")
        logging.info("Successfully configured. Please restart searchd.")

    def __create_sugg_index_config(self):
        fname = os.path.abspath(folders.temp + "/suggest.conf")
        logging.info("Creating config %s", fname)

        conf_data = template('aore/templates/sphinx/idx_suggest.conf', db_host=db_conf.host,
                             db_user=db_conf.user,
                             db_password=db_conf.password,
                             db_name=db_conf.database, db_port=db_conf.port,
                             index_name=sphinx_conf.index_sugg,
                             sphinx_var_path=sphinx_conf.var_dir)

        f = open(fname, "w")
        f.write(conf_data)
        f.close()

        logging.info("Done.")

        return fname

    def __dbexport_sugg_dict(self):
        logging.info("Place suggestion dict to DB %s...", self.files['dict.txt'])
        dict_dat_fname = os.path.abspath(folders.temp + "/suggdict.csv")

        csv_counter = 0
        with open(self.files['dict.txt'], "r") as dict_file, open(dict_dat_fname, "w") as exit_file:
            line = None
            while line != '':
                nodes = []
                line = dict_file.readline()
                if line == '':
                    break
                csv_counter += 1
                splitting_seq = line.split(' ')
                keyword = splitting_seq[0]
                freq = splitting_seq[1].rstrip('\n')
                assert keyword and freq, "Cannot process {}".format(self.files['dict.txt'])

                nodes.append(keyword)
                nodes.append(trigram(keyword))
                nodes.append(freq)

                exit_file.write("\t".join(nodes) + "\n")
        try:
            dict_file.close()
            exit_file.close()
        except:
            pass

        self.aodp.bulk_csv(AoXmlTableEntry.OperationType.update, "AOTRIG", csv_counter, dict_dat_fname)
        logging.info("Done.")

    def __create_ao_index_config(self):
        fname = os.path.abspath(folders.temp + "/addrobj.conf")
        logging.info("Creating config %s", fname)

        conf_data = template('aore/templates/sphinx/idx_addrobj.conf', db_host=db_conf.host,
                             db_user=db_conf.user,
                             db_password=db_conf.password,
                             db_name=db_conf.database, db_port=db_conf.port,
                             sql_query=template('aore/templates/postgre/sphinx_query.sql').replace("\n", " \\\n"),
                             index_name=sphinx_conf.index_addjobj,
                             sphinx_var_path=sphinx_conf.var_dir,
                             min_length_to_star=sphinx_conf.min_length_to_star)

        f = open(fname, "w")
        f.write(conf_data)
        f.close()

        logging.info("Done.")

        return fname

    def __create_suggestion_dict(self):
        fname = os.path.abspath(folders.temp + "/suggdict.txt")
        logging.info("Make suggestion dict (%s)...", fname)

        run_builddict_cmd = "{} {} -c {} --buildstops {} 200000 --buildfreqs".format(self.index_binary,
                                                                                     sphinx_conf.index_addjobj,
                                                                                     self.files['addrobj.conf'], fname)
        os.system(run_builddict_cmd)
        logging.info("Done.")

        return fname

    def __create_main_config(self, config_fname):
        out_filename = os.path.abspath(config_fname)
        logging.info("Creating main config %s...", out_filename)

        conf_data = template('aore/templates/sphinx/sphinx.conf', sphinx_listen=sphinx_conf.listen,
                             sphinx_var_path=sphinx_conf.var_dir)

        f = open(out_filename, "w")
        for fname, fpath in self.files.iteritems():
            if ".conf" in fname:
                with open(fpath, "r") as conff:
                    for line in conff:
                        f.write(line)
                    f.write('\n')
        f.write(conf_data)
        f.close()

        logging.info("Done.")

        return out_filename
