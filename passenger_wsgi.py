# -*- coding: utf-8 -*-

from aore import phias, config
from bottle import run

# Config section
# config.sphinx_conf.listen = "192.168.0.37:9312"
# config.sphinx_conf.var_dir = "C:\\Sphinx"
#
# config.db_conf.database = "pyfias"
# config.db_conf.host = "192.168.0.37"
# config.db_conf.port = 5432
# config.db_conf.user = "postgres"
# config.db_conf.password = "intercon"
#
# config.unrar_config.path = "C:\\Program Files (x86)\\WinRAR\\unrar.exe"
# config.folders.temp = "E:\\!TEMP"
#
# config.basic.logging = True

# Define main app
application = phias.App('test-config-fname')

# Run bottle WSGI server if no external
if __name__ == '__main__':
    application.start('0.0.0.0', 8087)
