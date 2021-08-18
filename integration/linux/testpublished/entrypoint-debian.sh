#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

install_ref="${PKG_INSTALL_REF}"

if [ -z "${install_ref}" ]; then
    echo ::error "Cannot determine package install ref."
    exit 1
fi

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
apt-get install -y curl gnupg apt-transport-https ncurses-bin
curl https://packages.edgedb.com/keys/edgedb.asc | apt-key add -
echo deb [arch=amd64] https://packages.edgedb.com/apt ${dist} main \
    >> /etc/apt/sources.list.d/edgedb.list

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

try=1
while [ $try -le 30 ]; do
    apt-get update && apt-get install -y "${install_ref}" && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

edgedb-server-${slot} --help
