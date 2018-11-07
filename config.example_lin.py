from aore import config

# Config section

# Address and port where sphinx was listening,
# may be a unix socket like 'unix:///tmp/fias-api.sock'
# or TCP socket like '127.0.0.1:9312'
config.SphinxConfig.listen = "unix:///tmp/fias-api.sock"
# Base sphinx folder
config.SphinxConfig.var_dir = "/etc/sphinx"

# DB config
config.DatabaseConfig.database = "fias_db"
config.DatabaseConfig.host = "127.0.0.1"
config.DatabaseConfig.port = 5432
config.DatabaseConfig.user = "postgres"
config.DatabaseConfig.password = "postgres"

# Path to unrar, in Linux may be 'unrar'
config.UnrarConfig.path = "unrar"
# Temp folder, in Linux may be '/tmp/myfolder'
config.Folders.temp = "/tmp/fitmp"

config.BasicConfig.logging = True
config.BasicConfig.debug_print = False
config.BasicConfig.logfile = "pyphias.log"
