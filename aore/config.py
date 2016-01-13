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
    ),
    production=dict(
        host="localhost",
        user="***",
        password="***",
        database="***",
    )
)

UNRAR_PATHES = dict(
    test="C:\Program Files (x86)\WinRAR\unrar.exe",
    production="unrar"
)

# Uncomment if you want to specify config_type manually
# config_type = "test"

# Main section
db = DB_INSTANCES[config_type]
unrar = UNRAR_PATHES[config_type]
trashfolder = "files/"
