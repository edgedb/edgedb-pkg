#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

wget -qO - https://packages.prod.edgedatabase.net/keys/edgedb.asc | apt-key add -
echo deb [arch=amd64] https://packages.prod.edgedatabase.net/apt ${DISTRO} main \
    >> /etc/apt/sources.list.d/edgedb.list
apt-get update
apt-get install -y edgedb-server
dpkg -i artifacts/edgedb-server_*_amd64.deb || apt-get -f install -y
edgedb-server --help
edgedb --help
