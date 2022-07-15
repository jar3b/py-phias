import re

from enum import Enum


class AoXmlTableOperationType(int, Enum):
    DELETE = 0
    UPDATE = 1
    CREATE = 2

    def __str__(self):
        return self.name


class AoXmlTableEntry:
    @classmethod
    def from_dir(cls, file_name, path):
        # for extracted into folder
        return AoXmlTableEntry(file_name, lambda: open(path + file_name, 'rb'))

    def __init__(self, file_name, lamda_open):
        matchings = re.search('^(AS_)(DEL_)*([A-Z]+)', file_name)

        self.table_name = matchings.group(3)
        self.operation_type = AoXmlTableEntry.OperationType(matchings.group(2) is None)

        self.lamda_open = lamda_open
        self.file_descriptor = None

    def open(self):
        if not self.file_descriptor:
            self.file_descriptor = self.lamda_open()

        return self.file_descriptor

    def close(self):
        self.file_descriptor.close()

    def __str__(self):
        return "Entry for {} table {}".format(self.operation_type, self.table_name)
