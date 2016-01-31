# -*- coding: utf-8 -*-

from platform import system

config_type = "production"
if "Windows" in system():
    config_type = "test"

DB_INSTANCES = dict(
    test=dict(
        host="localhost",
        user="postgres",
        password="intercon",
        database="postgres",
        port=5432
    ),
    production=dict(
        host="localhost",
        user="***",
        password="***",
        database="***",
        port=5432
    )
)

UNRAR_PATHES = dict(
    test="C:\Program Files (x86)\WinRAR\unrar.exe",
    production="unrar"
)

SPHINX_VAR_DIRS = dict(
    test="C:/Sphinx",
    production="/var/sphinx"
)

# Uncomment if you want to specify config_type manually
# config_type = "test"

# Main section
sphinx = dict(
    host_name="localhost",
    port=9312,
    index_addjobj="idx_fias_addrobj",
    index_sugg="idx_fias_sugg",
    var_dir=SPHINX_VAR_DIRS[config_type]
)

db = DB_INSTANCES[config_type]
unrar = UNRAR_PATHES[config_type]
trashfolder = "files/"
