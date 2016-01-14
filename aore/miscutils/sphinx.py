# -*- coding: utf-8 -*-

import logging
import os

from bottle import template

from aore.config import db as dbconfig, sphinx_index_addjobj, sphinx_var_dir, trashfolder


def configure_sphinx(indexer_binary):
    logging.info("Start configuring Sphinx...")

    # Create ADDROBJ config
    addrobj_cfg_name = get_addrobj_config()

    # Indexing it...
    run_index_cmd = "{} -c {} --all".format(indexer_binary, addrobj_cfg_name)
    logging.info("Run indexer (indexing ADDROBJ)...")
    os.system(run_index_cmd)
    logging.info("{} index was created.".format(sphinx_index_addjobj))

    # Produce dict file
    sugg_dict_name = get_suggestion_dict(indexer_binary, addrobj_cfg_name)


def get_suggestion_dict(indexer_binary, addrobj_cfg_name):
    logging.info("Make suggestion dict...")
    dict_file_name = os.path.abspath(trashfolder + "suggdict.txt")
    run_builddict_cmd = "{} {} -c {} --buildstops {} 200000 --buildfreqs".format(indexer_binary, sphinx_index_addjobj,
                                                                                 addrobj_cfg_name, dict_file_name)
    os.system(run_builddict_cmd)
    logging.info("Done.")

    return dict_file_name


def get_addrobj_config():
    config_fname = os.path.abspath(trashfolder + "addrobj.conf")
    logging.info("Creating config {}".format(config_fname))

    conf_data = template('aore/templates/sphinx/idx_addrobj.conf', db_host=dbconfig['host'], db_user=dbconfig['user'],
                         db_password=dbconfig['password'],
                         db_name=dbconfig['database'], db_port=dbconfig['port'],
                         sql_query=template('aore/templates/postgre/sphinx_query.sql').replace("\n", " \\\n"),
                         index_name=sphinx_index_addjobj,
                         sphinx_var_path=sphinx_var_dir)

    f = open(config_fname, "w")
    f.write(conf_data)
    f.close()

    logging.info("Done.")

    return config_fname


# TRASH
def produce_sphinx_config(config_name):
    conf_data = template('aore/templates/sphinx/sphinx.conf', sphinx_var_path=sphinx_var_dir)

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
