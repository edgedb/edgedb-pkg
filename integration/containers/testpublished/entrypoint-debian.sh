#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

slot="${PKG_VERSION_SLOT}"

if [ -z "${slot}" ]; then
    echo ::error "Cannot determine package version slot."
    exit 1
fi

dist="${PKG_PLATFORM_VERSION}"
if [ -n "${PKG_SUBDIST}" ]; then
    dist+=".${PKG_SUBDIST}"
fi

apt-get update
apt-get install -y curl gnupg apt-transport-https
curl https://packages.edgedb.com/keys/edgedb.asc | apt-key add -
echo deb [arch=amd64] https://packages.edgedb.com/apt ${dist} main \
    >> /etc/apt/sources.list.d/edgedb.list
apt-get update
apt-get install -y edgedb-${slot}
edgedb --help
