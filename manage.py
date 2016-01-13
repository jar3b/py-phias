# -*- coding: utf-8 -*-

import optparse

from aore.aoutils.aoupdater import AoUpdater
from aore.miscutils.sphinx import produce_sphinx_config


def update_base(xml_source, updates_count):
    aoupdater = AoUpdater(xml_source)
    aoupdater.update(updates_count)


def create_base(xml_source):
    aoupdater = AoUpdater(xml_source)
    aoupdater.create()


def main():
    # Parse options
    p = optparse.OptionParser()
    p.add_option('--database', '-b', action="store", type="string",
                 help="Manage database. Value: create - create new DB, update - update existing DB without loose the data")
    p.add_option('--update-count', '-u', default=1, type="int",
                 help="Count of updates to process, only for '--database update' option")
    p.add_option('--source', '-s', default="http",
                 help="Create/update DB from source. Value: \"http\" or absolute path to folder")
    p.add_option('--sphinx-configure', '-c', action="store", type="string",
                 help="Get Sphinx config. Value: /path/to/sphinx.conf")
    options, arguments = p.parse_args()

    if options.database:
        # create new database
        if options.database == "create":
            create_base(options.source)
        # update database
        if options.database == "update":
            update_base(options.source, int(options.update_count))

    if options.sphinx_configure:
        produce_sphinx_config(options.sphinx_configure)


if __name__ == '__main__':
    main()
