# -*- coding: utf-8 -*-


class DbSchema:
    def __init__(self, name, fieldlist, xmltag):
        self.tablename = name
        self.fields = fieldlist
        self.xml_tag = xmltag


db_shemas = dict()
db_shemas['ADDROBJ'] = DbSchema("ADDROBJ",
                                ["AOID", "AOGUID", "SHORTNAME", "FORMALNAME", "AOLEVEL", "PARENTGUID", "ACTSTATUS",
                                 "CURRSTATUS"],
                                "Object")
db_shemas['SOCRBASE'] = DbSchema("SOCRBASE", ["LEVEL", "SOCRNAME", "SCNAME", "KOD_T_ST"], "AddressObjectType")

allowed_tables = ["ADDROBJ", "SOCRBASE"]
