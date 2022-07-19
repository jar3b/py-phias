#!/bin/sh
docker build . -t pyphias:latest
cd deploy/sphinx
docker build . -t sphinx:latest
cd ../..
mkdir target
docker save pyphias:latest | gzip > target/pyphias_img.tar.gz
docker save sphinx:latest | gzip > target/sphinx_img.tar.gz
cp deploy/.env target/.env
cp deploy/docker-compose.yml target/docker-compose.yml
cp deploy/init.sh target/init.sh