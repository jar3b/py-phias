# -*- coding: utf-8 -*-

import optparse

from aore.fias.fiasfactory import FiasFactory
from aore.miscutils.sphinx import SphinxHelper
from aore.updater.updater import Updater
from aore.updater.soapreceiver import SoapReceiver


def print_fias_versions():
    imp = SoapReceiver()
    current_version = imp.get_current_fias_version()
    all_versions = imp.get_update_list()

    print("Installed version: {}".format(current_version))
    print("Avaliable updates:")
    print("Number\t\tDate")
    for upd in all_versions:
        mark_current = (' ', '*')[int(upd['intver']) == current_version]
        print "{}{}\t\t{}".format(mark_current, upd['intver'], upd['strver'])


def parse_update_str(updates_str):
    if updates_str == "all":
        return None

    upd_list = updates_str.lower().replace(' ','').split(',')
    out_list = []

    for u_entry in upd_list:
        if '-' in u_entry:
            u_range = u_entry.split('-')
            out_list += range(int(u_range[0]), int(u_range[1]))
        else:
            out_list.append(int(u_entry))

    return out_list


def get_allowed_updates(updates_str, mode = "create"):
    imp = SoapReceiver()
    current_version = imp.get_current_fias_version()
    all_versions = [x for x in imp.get_update_list()]

    user_defined_list = parse_update_str(updates_str)
    out_list = []

    if mode == "create" and not user_defined_list:
        yield all_versions[-1]

    assert (mode == "create" and len(user_defined_list) == 1)

    for uv in all_versions:
        uv_ver = uv['intver']
        if uv_ver > current_version and (not user_defined_list or uv_ver in user_defined_list):
            out_list.append(uv)

    out_list.sort(key=lambda x: x['intver'])
    for ol_entry in out_list:
        yield ol_entry


def main():
    # Parse options
    p = optparse.OptionParser()
    p.add_option('--database', '-b', action="store", type="string",
                 help="Manage database. Values: "
                      "create - create new DB, "
                      "update - update existing DB without loose the data")
    p.add_option('--update-version', '-u', default="all", type="string",
                 help="Valid for updating via HTTP. "
                      "Versions of updates to process. Can be 111 or 111-222 or 111,222,333."
                      "For '--database-create' only one value is necessary. If not specified, "
                      "all updates will be processed (for '--database update') or last DB snapshot "
                      "(for '--database create')")
    p.add_option('--show-versions', '-v', action="store_true", dest="show_versions", default=False,
                 help="Show allowed fias versions")
    p.add_option('--source', '-s', default="http",
                 help="Create/update DB from source. Value: 'http' or absolute path to folder containing XMLs")
    p.add_option('--sphinx-configure', '-c', action="store_true", dest="sphinx", default="False",
                 help="Configure sphinx. Creates sphinx.conf specified in '--output-conf'")
    p.add_option('--indexer-path', '-i',
                 help="Path to sphinx indexer binary. Required for '--sphinx-configure'")
    p.add_option('--output-conf', '-o',
                 help="Output config filename. Required for '--sphinx-configure'")
    p.add_option('--test', '-t', action="store_true", dest="test",
                 help="Test")

    options, arguments = p.parse_args()

    # Show FIAS updates
    if options.show_versions:
        print_fias_versions()
        return

    # Manage DB
    if options.database:
        # create new database
        aoupdater = Updater(options.source)
        allowed_updates = None
        if options.source == "http":
            allowed_updates = get_allowed_updates(options.update_version)

        if options.database == "create":
            aoupdater.create(allowed_updates)

        # update database
        if options.database == "update":
            aoupdater.update(allowed_updates)

    # Manage Sphinx
    if options.sphinx and options.indexer_path and options.output_conf:
        sphinxh = SphinxHelper()
        sphinxh.configure_indexer(options.indexer_path, options.output_conf)

    # 4 Debug purposes..
    if options.test:
        sph = FiasFactory()
        sph.find('ул кемровая пасраул алтай майминский р-н')


if __name__ == '__main__':
    main()
