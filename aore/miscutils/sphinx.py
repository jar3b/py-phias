# -*- coding: utf-8 -*-

import logging
import os

from bottle import template

from aore.config import db as dbconfig, sphinx_index_name, sphinx_var_dir


def produce_sphinx_config(config_name):
    logging.info("Creating {}".format(config_name))
    conf_data = template('aore/templates/sphinx/data.conf', db_host=dbconfig['host'], db_user=dbconfig['user'],
                         db_password=dbconfig['password'],
                         db_name=dbconfig['database'], db_port=dbconfig['port'],
                         sql_query=template('aore/templates/postgre/sphinx_query.sql').replace("\n"," \\\n"), index_name=sphinx_index_name,
                         sphinx_var_path=sphinx_var_dir)

    conf_data += "\n" + template('aore/templates/sphinx/sphinx.conf', sphinx_var_path=sphinx_var_dir)

    if os.path.isfile(config_name):
        choice = raw_input(
            "WARNING! File {} already exists. It will be overwritten, "
            "all settings all setting will be lost! Are you sure? [y/n]: ".format(
                config_name))
        if choice.lower() != 'y':
            logging.warning("Aborted.")
            return

    conf_file = open(config_name, "w")
    conf_file.write(conf_data)
    conf_file.close()

    logging.info("Success! Re-index db: \n"
                 "\t$indexer -c {} --all --rotate\n"
                 "and then re/start your Sphinx:\n"
                 "\t$/etc/init.d/sphinxsearch stop\n"
                 "\t$/etc/init.d/sphinxsearch start".format(config_name))
