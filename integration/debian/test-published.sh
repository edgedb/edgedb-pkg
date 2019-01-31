#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y curl gnupg
curl https://packages.prod.edgedatabase.net/keys/edgedb.asc | apt-key add -
echo deb [arch=amd64] https://packages.prod.edgedatabase.net/apt ${DISTRO} main \
    >> /etc/apt/sources.list.d/edgedb.list
apt-get remove -y curl gnupg
apt-get autoremove -y
apt-get update
apt-get install -y edgedb-server
edgedb-server --help
edgedb --help
