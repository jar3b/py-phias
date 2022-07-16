import re

from pathlib import Path
from typing import Callable, BinaryIO


class AoXmlTableEntry:
    __slots__ = ['is_delete', 'table_name', 'lambda_open', 'obj']
    is_delete: bool
    table_name: str
    lambda_open: Callable[[], BinaryIO]
    obj: BinaryIO | None

    def __init__(self, file_name: str, lambda_open: Callable[[], BinaryIO]) -> None:
        name_parts = re.search('^(AS_)(DEL_)*([A-Z]+)', file_name)
        if not name_parts:
            raise Exception(f'Invalid table name {file_name}, has no "^(AS_)(DEL_)*([A-Z]+)" pattern')

        self.table_name = name_parts.group(3)
        self.is_delete = name_parts.group(2) is not None
        self.lambda_open = lambda_open  # type: ignore
        self.obj = None

    @classmethod
    def from_dir(cls, path: Path) -> 'AoXmlTableEntry':
        # for extracted into folder
        return AoXmlTableEntry(path.name, lambda: path.open('rb'))

    @property
    def op_name(self) -> str:
        return "DELETE" if self.is_delete else "CREATE"

    def open(self) -> BinaryIO:
        self.obj = self.lambda_open()  # type: ignore
        return self.obj

    def close(self) -> None:
        if self.obj:
            self.obj.close()

    def __str__(self) -> str:
        return f'Entry {self.op_name} "{self.table_name}"'
