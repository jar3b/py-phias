# -*- coding: utf-8 -*-

import optparse

from aore.aoutils.aoupdater import AoUpdater


def update_base(updates_count):
    aoupdater = AoUpdater()
    aoupdater.update_db(updates_count)


def create_base(path_to_xmls):
    aoupdater = AoUpdater(path_to_xmls)
    aoupdater.create()


def main():
    # Parse options
    p = optparse.OptionParser()
    p.add_option('--create', '-c', help="Create DB from official full XMLs; "
                                        "CREATE = path to xml source dir")
    p.add_option('--update', '-u', help="Update DB from official delta archive; "
                                        "UPDATE = count of updates")
    options, arguments = p.parse_args()

    # create new database
    if options.create:
        create_base(options.create)
    # update database
    if options.update:
        update_base(int(options.update))


if __name__ == '__main__':
    main()
