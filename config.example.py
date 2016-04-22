# -*- coding: utf-8 -*-
from aore import config

# Config section

# Address and port where sphinx was listening,
# may be a unix socket like 'unix://tmp/pyphias.sock'
config.SphinxConfig.listen = "127.0.0.1:9312"
# Base sphinx folder
config.SphinxConfig.var_dir = "C:\\Sphinx"

# DB config
config.DatabaseConfig.database = "fias_db"
config.DatabaseConfig.host = "192.168.0.1"
config.DatabaseConfig.port = 5432
config.DatabaseConfig.user = "postgres"
config.DatabaseConfig.password = "postgres"

# Path to unrar, in Linux may be 'unrar'
config.UnrarConfig.path = "C:\\Program Files\\WinRAR\\unrar.exe"
# Temp folder, in Linux may be '/tmp/myfolder'
config.Folders.temp = "E:\\!TEMP"

config.BasicConfig.logging = True
config.BasicConfig.debug_print = False
config.BasicConfig.logfile = "pyphias.log"
