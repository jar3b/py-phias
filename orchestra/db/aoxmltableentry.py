from typing import Callable, BinaryIO, IO


class AoXmlTableEntry:
    __slots__ = ['is_delete', 'file_name', 'table_name', 'lambda_open', 'obj']
    is_delete: bool
    file_name: str
    table_name: str
    lambda_open: Callable[[], IO]
    obj: IO | None

    def __init__(self, f_name: str, table_name: str, is_delete: bool, *, lambda_open: Callable[[], IO]) -> None:
        self.file_name = f_name
        self.table_name = table_name
        self.is_delete = is_delete
        self.lambda_open = lambda_open  # type: ignore
        self.obj = None

    @property
    def op_name(self) -> str:
        return "DELETE" if self.is_delete else "CREATE"

    def open(self) -> IO:
        self.obj = self.lambda_open()  # type: ignore
        return self.obj

    def close(self) -> None:
        if self.obj:
            self.obj.close()

    def __str__(self) -> str:
        return f'Entry {self.op_name} "{self.table_name}"'
