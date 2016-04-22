# -*- coding: utf-8 -*-


class BasicConfig:
    logging = False
    debug_print = False
    logfile = ""

    def __init__(self):
        pass


class SphinxConfig:
    listen = "127.0.0.1:9312"
    index_addjobj = "idx_fias_addrobj"
    index_sugg = "idx_fias_sugg"
    var_dir = None
    min_length_to_star = 3

    def __init__(self):
        pass


class DatabaseConfig:
    host = None
    user = None
    password = None
    database = None
    port = None

    def __init__(self):
        pass


class UnrarConfig:
    path = None

    def __init__(self):
        pass


class Folders:
    temp = None

    def __init__(self):
        pass
