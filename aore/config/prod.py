# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .common import *

sphinx_conf.host_name = "localhost"
sphinx_conf.port = 9312
sphinx_conf.var_dir = "/var/sphinx"

db_conf.database = "postgres"
db_conf.host = "localhost"
db_conf.port = 5432
db_conf.user = "postgres"
db_conf.password = "postgres"

unrar_config.path = "unrar"
folders.temp = "/tmp/py-fias"
