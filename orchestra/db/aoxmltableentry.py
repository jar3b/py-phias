import re

from pathlib import Path
from typing import Callable, BinaryIO


class AoXmlTableEntry:
    __slots__ = ['is_delete', 'table_name', 'lambda_open']
    is_delete: bool
    table_name: str
    lambda_open: Callable[[], BinaryIO]

    def __init__(self, file_name: str, lambda_open: Callable[[], BinaryIO]) -> None:
        name_parts = re.search('^(AS_)(DEL_)*([A-Z]+)', file_name)

        self.table_name = name_parts.group(3)
        self.is_delete = name_parts.group(2) is not None
        self.lambda_open = lambda_open

    @classmethod
    def from_dir(cls, path: Path) -> 'AoXmlTableEntry':
        # for extracted into folder
        return AoXmlTableEntry(path.name, lambda: path.open('rb'))

    def __str__(self):
        return f'Entry {"DELETE" if self.is_delete else "CREATE"} "{self.table_name}"'
