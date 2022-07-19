#!/bin/sh
SUGG_TXT=suggdict.txt
mkdir -p ./data/source
read -p "Place XML files onto './data/source' and press [Enter] ..."
docker-compose up -d db
docker-compose run -ti --rm app initdb -f "/source" -t "/temp" --container-temp "/temp"
docker-compose run --rm app create-addrobj-config -f idx_addrobj.conf -t "./temp" --container-temp "/temp" --sphinx-var="${SPHINX_VAR}"
docker-compose run -ti --rm sphinx indexer idx_fias_addrobj -c /temp/idx_addrobj.conf --buildstops /temp/${SUGG_TXT} 200000 --buildfreqs
rm ./data/temp/idx_addrobj.conf
docker-compose run -ti --rm app init-trigram -f ${SUGG_TXT} -t "/temp" --container-temp "/temp"
docker-compose run -ti --rm app create-sphinx-config -f "/etc/sphinxsearch/sphinx.conf" --sphinx-var="/var/lib/sphinxsearch"
docker-compose run -ti --rm sphinx indexer -c /etc/sphinxsearch/sphinx.conf --all --rotate
docker-compose up -d sphinx
docker-compose up -d app