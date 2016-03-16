# -*- coding: utf-8 -*-


class BasicConfig:
    def __init__(self):
        self.logging = False
        self.logfile = ""

class SphinxConfig:
    def __init__(self):
        self.listen = "127.0.0.1:9312"
        self.index_addjobj = "idx_fias_addrobj"
        self.index_sugg = "idx_fias_sugg"
        self.var_dir = None
        self.min_length_to_star = 3

class DatabaseConfig:
    def __init__(self):
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.port = None

class UnrarConfig:
    def __init__(self):
        self.path = None


class Folders:
    def __init__(self):
        self.temp = None
