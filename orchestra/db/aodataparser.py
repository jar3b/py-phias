import io
from pathlib import Path
from typing import List, Callable, Dict, Any, Awaitable

from .aoxmltableentry import AoXmlTableEntry
from .named_bytes import NamedBytes
from .schemas import DB_SCHEMAS
from .xmlparser import XMLParser


class AoDataParser:
    __slots__ = [
        'table_entry', 'allowed_fields', 'page_size', 'counter', 'current_page', 'base_csv_filename',
        'csv_file'
    ]

    table_entry: AoXmlTableEntry
    allowed_fields: List[str]
    page_size: int
    temp_folder: Path

    counter: int
    current_page: int
    base_csv_filename: str
    csv_file: NamedBytes | None

    def __init__(self, table_entry: AoXmlTableEntry, page_size: int) -> None:
        self.table_entry = table_entry
        if table_entry.table_name not in DB_SCHEMAS:
            raise Exception(f"Cannot parse table {table_entry.table_name}: Not configured.")

        # check table has XML_TAG
        if DB_SCHEMAS[self.table_entry.table_name].xml_tag is None:
            raise Exception(f'Table {table_entry.table_name} has no xml_tag')

        # set allowed columns to insert
        self.allowed_fields = DB_SCHEMAS[table_entry.table_name].columns
        self.page_size = page_size

        # path params
        self.counter = 0
        self.current_page = 0
        self.base_csv_filename = f'fd_{self.table_entry.op_name}_{self.table_entry.table_name}.part{{}}.csv'
        self.csv_file = None

    # Output - sql query
    async def parse(self, data_callback: Callable[[int, NamedBytes], Awaitable[None]]) -> None:
        async def refresh_csv() -> None:
            if self.csv_file:
                await data_callback(self.counter, self.csv_file)
                self.csv_file.data.close()
                del self.csv_file.data
                del self.csv_file
                self.csv_file = None

        async def import_update(attr: Dict[str, Any]) -> None:
            if self.counter >= self.page_size:
                # Send old file to DB engine
                if self.csv_file:
                    await refresh_csv()

                # Prepare to next iteration
                self.counter = 0
                self.current_page += 1
                self.csv_file = NamedBytes(self.base_csv_filename.format(self.current_page), io.BytesIO())

            if not self.csv_file:
                self.csv_file = NamedBytes(self.base_csv_filename.format(self.current_page), io.BytesIO())

            exit_nodes: List[Any] = []
            for allowed_field in self.allowed_fields:
                if allowed_field in attr:
                    exit_nodes.append(attr[allowed_field])
                else:
                    exit_nodes.append("NULL")

            exit_string = "\t".join(exit_nodes)
            self.csv_file.data.writelines([exit_string.encode('utf-8')])
            self.counter += 1

        xml_parser = XMLParser(import_update)
        src = self.table_entry.open()
        try:
            await xml_parser.parse_buffer(src, DB_SCHEMAS[self.table_entry.table_name].xml_tag)  # type: ignore
        finally:
            src.close()

        # Send last file to db processor
        if self.csv_file:
            await refresh_csv()
