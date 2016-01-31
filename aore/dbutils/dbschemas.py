# -*- coding: utf-8 -*-


class DbSchema:
    def __init__(self, name, fieldlist, unique_key, xmltag):
        self.tablename = name
        self.fields = fieldlist
        self.unique_field = unique_key
        self.xml_tag = xmltag


db_shemas = dict()
db_shemas['ADDROBJ'] = DbSchema("ADDROBJ",
                                ["AOID", "AOGUID", "SHORTNAME", "FORMALNAME", "AOLEVEL", "PARENTGUID", "ACTSTATUS",
                                 "LIVESTATUS", "NEXTID"],
                                "aoid",
                                "Object")
db_shemas['SOCRBASE'] = DbSchema("SOCRBASE", ["LEVEL", "SOCRNAME", "SCNAME", "KOD_T_ST"], "kod_t_st",
                                 "AddressObjectType")

db_shemas['AOTRIG'] = DbSchema("AOTRIG", ["WORD", "TRIGRAMM", "FREQUENCY"], "word",
                               None)

allowed_tables = ["ADDROBJ", "SOCRBASE"]
