from typing import List


class DbSchema:
    __slots__ = ['table', 'columns', 'pk', 'xml_tag']
    table: str
    columns: List[str]
    pk: str
    xml_tag: str | None

    def __init__(self, name: str, columns: List[str], pk: str, xml_tag: str | None) -> None:
        self.table = name
        self.columns = columns
        self.pk = pk
        self.xml_tag = xml_tag


DB_SCHEMAS = {
    'ADDROBJ': DbSchema(
        "ADDROBJ",
        ["AOID", "AOGUID", "SHORTNAME", "FORMALNAME", "AOLEVEL", "PARENTGUID", "ACTSTATUS",
         "LIVESTATUS",
         "NEXTID", "REGIONCODE"],
        "aoid",
        "Object"
    ),
    'SOCRBASE': DbSchema(
        "SOCRBASE",
        ["LEVEL", "SOCRNAME", "SCNAME", "KOD_T_ST"],
        "kod_t_st",
        "AddressObjectType"
    ),
    'AOTRIG': DbSchema(
        "AOTRIG", ["WORD", "TRIGRAMM", "FREQUENCY"],
        "word",
        None
    )
}

ALLOWED_TABLES = ["ADDROBJ", "SOCRBASE"]
