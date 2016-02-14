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
        self.fname = None
        self.mode = None

    def local(self, fname):
        self.fname = fname
        self.mode = "local"

    def download(self, url):
        logging.info("Downloading %s", url)
        try:
            local_filename = os.path.abspath(folders.temp + "/" + url.split('/')[-1])
            if os.path.isfile(local_filename):
                os.remove(local_filename)
            else:
                if not os.path.exists(folders.temp):
                    os.makedirs(folders.temp)

            request = requests.get(url, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in request.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            raise FiasException("Error downloading. Reason : {}".format(format_exc()))

        logging.info("Downloaded %d bytes", int(request.headers['Content-length']))
        self.fname = local_filename
        self.mode = "remote"

    def get_table_entries(self, allowed_tables):
        if self.fname and os.path.isfile(self.fname):
            rf = rarfile.RarFile(self.fname)

            for arch_entry in rf.infolist():
                xmltable = AoXmlTableEntry.from_rar(arch_entry.filename, rf, arch_entry)
                if xmltable.table_name in allowed_tables:
                    yield xmltable
            else:
                logging.info("All entries processed")
                if self.mode == "remote":
                    try:
                        os.remove(self.fname)
                    except:
                        logging.warning("Cannot delete %s, do it manually", self.fname)
        else:
            logging.error("No file specified or not exists")
