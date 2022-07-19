#!/bin/sh
set -e

chown -R sphinxsearch:root /run/sphinxsearch
if [ "$1" = 'searchd' ]; then
  #indexer -c /etc/sphinxsearch/sphinx.conf --all --rotate
  echo "Indexing done"
fi

exec "$@"