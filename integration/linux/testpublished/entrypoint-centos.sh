#!/bin/bash

set -ex

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

repo="edgedb"
if [ -n "${PKG_SUBDIST}" ]; then
    repo+="-${PKG_SUBDIST}"
fi

curl -fL https://packages.edgedb.com/rpm/edgedb-rhel.repo \
    >/etc/yum.repos.d/edgedb.repo

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

try=1
while [ $try -le 30 ]; do
    yum makecache \
    && yum install --enablerepo="${repo}" --verbose -y "${install_ref}" \
    && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

edgedb-server-${slot} --help
