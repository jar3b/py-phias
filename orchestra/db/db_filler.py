from pathlib import Path

from settings import AppConfig


class DbFiller:
    __slots__ = ['conf']
    conf: AppConfig

    def __init__(self, conf: AppConfig) -> None:
        self.conf = conf

    async def create(self, source: Path) -> None:
        pass

    def __get_entries_from_folder(self, path_to_xmls) -> Iterator[AoXmlTableEntry]:
        for (dirpath, dirnames, filenames) in walk(path_to_xmls):
            for filename in filenames:
                if filename.endswith(".XML"):
                    xmltable = AoXmlTableEntry.from_dir(filename, dirpath.replace("\\", "/") + "/")
                    if xmltable.table_name in allowed_tables:
                        yield xmltable
            break