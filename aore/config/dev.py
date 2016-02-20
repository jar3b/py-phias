# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .common import *

sphinx_conf.listen = "127.0.0.1:9312"
sphinx_conf.var_dir = "C:\\Sphinx"

db_conf.database = "postgres"
db_conf.host = "localhost"
db_conf.port = 5432
db_conf.user = "postgres"
db_conf.password = "intercon"

unrar_config.path = "C:\\Program Files (x86)\\WinRAR\\unrar.exe"
folders.temp = "E:\\!TEMP"

basic.logging = True
