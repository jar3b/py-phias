# -*- coding: utf-8 -*-
from aore import config

# Config section
config.sphinx_conf.listen = "127.0.0.1:9312"
config.sphinx_conf.var_dir = "C:\\Sphinx"

config.db_conf.database = "pyfias"
config.db_conf.host = "192.168.0.1"
config.db_conf.port = 5432
config.db_conf.user = "postgres"
config.db_conf.password = "postgres"

config.unrar_config.path = "C:\\Program Files\\WinRAR\\unrar.exe"
config.folders.temp = "E:\\!TEMP"

config.basic.logging = True
