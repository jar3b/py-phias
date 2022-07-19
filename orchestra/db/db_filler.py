import os
import re
import zipfile
from abc import abstractmethod
from pathlib import Path
from typing import Iterator, Any, Awaitable, Callable, Tuple, Optional

import asyncpg
import click
from jinja2 import Environment, FileSystemLoader

from settings import AppConfig
from .aodataparser import AoDataParser
from .aoxmltableentry import AoXmlTableEntry
from .named_bytes import NamedBytes
from .schemas import ALLOWED_TABLES, DB_SCHEMAS


class Source:
    __slots__ = ['path']
    path: Path

    def __init__(self, p: Path):
        self.path = p

    @classmethod
    @abstractmethod
    def from_path(cls, p: Path) -> Optional['Source']:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    # returns [table_name, is_delete] for file_name
    def _parse_name(name: str) -> Tuple[str | None, bool]:
        raise NotImplementedError()

    @abstractmethod
    def get_table_iterator(self) -> Iterator[AoXmlTableEntry]:
        raise NotImplementedError()

    @abstractmethod
    async def generate_csv(
            self,
            table_entry: AoXmlTableEntry,
            data_callback: Callable[[int, NamedBytes], Awaitable[None]],
    ) -> None:
        raise NotImplementedError()


class CsvXmlSource(Source):
    __slots__ = ['zip_file']
    MATCH_STR = f'fd_(CREATE|DELETE)_({"|".join(ALLOWED_TABLES)})\\.part[0-9]+\\.csv'

    def __init__(self, p: Path, zip_file: Path):
        super().__init__(p)
        self.zip_file = zip_file

    @staticmethod
    def _parse_name(name: str) -> Tuple[str | None, bool]:
        m = re.search(CsvXmlSource.MATCH_STR, name)
        if not m:
            return None, False

        return m.group(2), m.group(1) == 'DELETE'

    def get_table_iterator(self) -> Iterator[AoXmlTableEntry]:
        with zipfile.ZipFile(self.zip_file) as zf:
            for zip_entry in zf.namelist():
                table_info = CsvXmlSource._parse_name(zip_entry)
                if table_info[0]:
                    yield AoXmlTableEntry(zip_entry, table_info[0], table_info[1],
                                          lambda_open=lambda: zf.open(zip_entry, 'r'))

    @classmethod
    def from_path(cls, p: Path) -> Optional['CsvXmlSource']:
        zip_files = list(p.glob('*.zip'))
        if len(zip_files) != 1:
            return None
        zip_file = zip_files[0]

        names = [CsvXmlSource._parse_name(x)[0] for x in zipfile.ZipFile(zip_file).namelist()]
        if all({x: x in names for x in ALLOWED_TABLES}.values()):
            return CsvXmlSource(p, zip_file)

    async def generate_csv(
            self,
            table_entry: AoXmlTableEntry,
            data_callback: Callable[[int, NamedBytes], Awaitable[None]]
    ) -> None:
        with table_entry.lambda_open() as f:  # type: ignore
            await data_callback(0, NamedBytes(table_entry.file_name, f))


class XmlListSource(Source):
    MATCH_STR = f'(AS|DEL)_({"|".join(ALLOWED_TABLES)})_([0-9]{{8}})_([a-z0-9-]+)\\.XML'

    def get_table_iterator(self) -> Iterator[AoXmlTableEntry]:
        for xml_file in self.path.glob("*.XML"):
            table_info = self._parse_name(xml_file.name)
            if table_info[0]:
                yield AoXmlTableEntry(xml_file.name, table_info[0], table_info[1],
                                      lambda_open=lambda: xml_file.open('rb'))

    @staticmethod
    def _parse_name(name: str) -> Tuple[str | None, bool]:
        m = re.search(XmlListSource.MATCH_STR, name)
        if not m:
            return None, False

        return m.group(2), m.group(1) == 'DEL'

    @classmethod
    def from_path(cls, p: Path) -> Optional['XmlListSource']:
        names = [XmlListSource._parse_name(x.name)[0] for x in p.glob("*.XML")]
        if all({x: x in names for x in ALLOWED_TABLES}.values()):
            return XmlListSource(p)

    async def generate_csv(
            self,
            table_entry: AoXmlTableEntry,
            data_callback: Callable[[int, NamedBytes], Awaitable[None]]
    ) -> None:
        ao_parser = AoDataParser(table_entry, 50000)
        await ao_parser.parse(data_callback)


class DbFiller:
    __slots__ = ['conf', 'tpl_env', 'pool', 'indexes_dropped']
    conf: AppConfig
    tpl_env: Environment
    pool: asyncpg.Pool
    indexes_dropped: bool

    def __init__(self, conf: AppConfig) -> None:
        self.tpl_env = Environment(loader=FileSystemLoader('orchestra/templates'))
        self.conf = conf
        self.indexes_dropped = False

    async def __init_pg_pool(self) -> None:
        # create pool
        conf = self.conf.pg
        dsn = f'postgres://{conf.user}:{conf.password}@{conf.host}:{conf.port}/{conf.name}'
        self.pool = await asyncpg.create_pool(dsn, max_inactive_connection_lifetime=conf.pool_recycle)

    def __ensure_source(self, source_path: Path) -> Source:
        _sources = [y for y in [x.from_path(source_path) for x in [CsvXmlSource, XmlListSource]] if y]
        if len(_sources) == 0:
            raise Exception(f'"{source_path}" is not valid (no XML or ZIP inside)')
        if len(_sources) > 1:
            raise Exception(f'"{source_path}" has multiple roles: {", ".join([str(type(x)) for x in _sources])}')

        return _sources[0]

    async def create(self, source_path: Path, temp_folder: Path, pg_folder: Path) -> None:
        # check source type
        source = self.__ensure_source(source_path)

        await self.__init_pg_pool()

        try:
            # create tables
            await self.__run_query('create_structure.sql')
            # drop indexes
            await self.__run_query('drop_indexes.sql')
            # fill data
            for table_entry in source.get_table_iterator():
                await source.generate_csv(table_entry, self.__bulk_insert_wrapper(
                    table_entry, pg_folder, temp_folder
                ))
            # create indexes
            await self.__run_query('create_indexes.sql')
        finally:
            await self.pool.close()

    async def create_csv_zip(self, source_path: Path, target: Path) -> None:
        source = self.__ensure_source(source_path)

        # get entities from folder
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for table_entry in source.get_table_iterator():
                await source.generate_csv(table_entry, self.__create_zip_wrapper(
                    zf
                ))

    def __create_zip_wrapper(self, zf: zipfile.ZipFile) -> Callable[
        [int, NamedBytes], Awaitable[None]
    ]:
        async def on_csv_received(items_count: int, csv_file: NamedBytes) -> None:
            click.echo(f'Processing "{csv_file.name}" with {items_count} items...')
            csv_file.data.seek(0)
            zf.writestr(csv_file.name, csv_file.data.read(), compresslevel=7)

        return on_csv_received

    def __bulk_insert_wrapper(self, table_entry: AoXmlTableEntry, pg_folder: Path, temp_folder: Path) -> Callable[
        [int, NamedBytes], Awaitable[None]
    ]:
        async def bulk_insert_csv(items_count: int, csv_file: NamedBytes) -> None:
            click.echo(f'Processing "{csv_file.name}" with {items_count} items...')
            csv_file.data.seek(0)
            temp_saved_csv = Path(temp_folder, csv_file.name)
            pg_alias_csv = Path(pg_folder, csv_file.name)

            with temp_saved_csv.open('wb') as f:
                f.write(csv_file.data.read())

            try:
                if table_entry.is_delete:
                    await self.__run_query(
                        'bulk_delete.sql',
                        delim='\t',
                        tablename=table_entry.table_name,
                        fieldslist=", ".join(DB_SCHEMAS[table_entry.table_name].columns),
                        csvname=pg_alias_csv.as_posix(),
                        uniquekey=DB_SCHEMAS[table_entry.table_name].pk
                    )
                else:
                    await self.__run_query(
                        'bulk_create.sql',
                        delim='\t',
                        tablename=table_entry.table_name,
                        fieldslist=", ".join(DB_SCHEMAS[table_entry.table_name].columns),
                        csvname=pg_alias_csv.as_posix()
                    )
                click.echo(f'"{temp_saved_csv}" as {pg_alias_csv.as_posix()} executed')
            finally:
                os.remove(temp_saved_csv)

        return bulk_insert_csv

    async def create_table_from_csv(self, pg_folder: Path, csv_file_path: Path, table_name: str) -> None:
        await self.__init_pg_pool()

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(f'TRUNCATE "{table_name}";')

            await self.__run_query(
                'bulk_create.sql',
                delim='\t',
                tablename=table_name,
                fieldslist=", ".join(DB_SCHEMAS[table_name].columns),
                csvname=Path(pg_folder, csv_file_path.name).as_posix()
            )
        finally:
            await self.pool.close()

    async def __run_query(self, template_name: str, *args: Any, **kwargs: Any) -> None:
        click.echo(f'Executing "{template_name}"...')

        query = self.tpl_env.get_template(template_name).render(*args, **kwargs)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query)

        click.echo(f'Template "{template_name}" executed into db')
