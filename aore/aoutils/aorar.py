# -*- coding: utf-8 -*-

import os.path
from traceback import format_exc

import rarfile
import requests

from aore.config import unrar, trashfolder
from aoxmltableentry import AoXmlTableEntry


class AoRar:
    def __init__(self):
        rarfile.UNRAR_TOOL = unrar

    def download(self, url):
        print("Downloading {}".format(url))
        try:
            local_filename = os.path.abspath(trashfolder + url.split('/')[-1])
            if os.path.isfile(local_filename):
                return local_filename
                os.remove(local_filename)

            request = requests.get(url, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in request.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except:
            print("Error downloading. Reason : {}".format(format_exc()))
            return None

        print("Downloaded {} bytes".format(request.headers['Content-length']))
        return local_filename

    def get_table_entries(self, file_name, allowed_tables):
        if file_name and os.path.isfile(file_name):
            rf = rarfile.RarFile(file_name)

            for arch_entry in rf.infolist():
                xmltable = AoXmlTableEntry.from_rar(arch_entry.filename, rf, arch_entry)
                if xmltable.table_name in allowed_tables:
                    yield xmltable
            else:
                print "Done"
                # os.remove(file_name) TODO : Uncomment
        else:
            print("No file specified or not exists")
