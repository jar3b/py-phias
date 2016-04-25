# bind = "127.0.0.1:8888"
bind = "unix:/tmp/fias-api-unicorn.sock"
workers = 5
user = "fias"
group = "fias"
logfile = "/var/log/gunicorn.log"
loglevel = "info"
