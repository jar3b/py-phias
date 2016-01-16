# -*- coding: utf-8 -*-

import optparse

from aore.aoutils.aoupdater import AoUpdater
from aore.miscutils.sphinx import SphinxHelper
from aore.fias.search import SphinxSearch


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
    p.add_option('--sphinx-configure', '-c', action="store_true", dest="sphinx", default="False",
                 help="Configure sphinx. Creates sphinx.conf specified in '--output-conf'")
    p.add_option('--indexer-path', '-i',
                 help="Path to sphinx indexer binary. Required for '--sphinx-configure'")
    p.add_option('--output-conf', '-o',
                 help="Output config filename. Required for '--sphinx-configure'")
    p.add_option('--test', '-t', action="store_true", dest="test",
                 help="Test")

    options, arguments = p.parse_args()

    # Manage DB
    if options.database:
        # create new database
        if options.database == "create":
            create_base(options.source)
        # update database
        if options.database == "update":
            update_base(options.source, int(options.update_count))

    # Manage Sphinx
    if options.sphinx and options.indexer_path and options.output_conf:
        sphinxh = SphinxHelper()
        sphinxh.configure_indexer(options.indexer_path, options.output_conf)

    # 4 Debug purposes..
    if options.test:
        sph = SphinxSearch()
        sph.find('#москва$#северное тушино$$$ул#туристская')

if __name__ == '__main__':
    main()
