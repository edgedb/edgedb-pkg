#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y curl gnupg apt-transport-https
curl https://packages.edgedb.com/keys/edgedb.asc | apt-key add -
echo deb [arch=amd64] https://packages.edgedb.com/apt ${DISTRO} main \
    >> /etc/apt/sources.list.d/edgedb.list
apt-get remove -y curl gnupg
apt-get autoremove -y
apt-get update
apt-get install -y edgedb-1-alpha1
edgedb --help
