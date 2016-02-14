# -*- coding: utf-8 -*-

import logging
import os.path
from traceback import format_exc

import rarfile
import requests

from aore.config import folders, unrar_config
from aore.miscutils.exceptions import FiasException
from aoxmltableentry import AoXmlTableEntry


class AoRar:
    def __init__(self):
        rarfile.UNRAR_TOOL = unrar_config.path

    def download(self, url):
        logging.info("Downloading %s", url)
        try:
            local_filename = os.path.abspath(folders.temp + "/" + url.split('/')[-1])
            if os.path.isfile(local_filename):
                os.remove(local_filename)
            else:
                os.makedirs(local_filename)

            request = requests.get(url, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in request.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            raise FiasException("Error downloading. Reason : {}".format(format_exc()))

        logging.info("Downloaded %d bytes", int(request.headers['Content-length']))
        return local_filename

    def get_table_entries(self, file_name, allowed_tables):
        if file_name and os.path.isfile(file_name):
            rf = rarfile.RarFile(file_name)

            for arch_entry in rf.infolist():
                xmltable = AoXmlTableEntry.from_rar(arch_entry.filename, rf, arch_entry)
                if xmltable.table_name in allowed_tables:
                    yield xmltable
            else:
                logging.info("All entries processed")
                os.remove(file_name)
        else:
            logging.error("No file specified or not exists")
