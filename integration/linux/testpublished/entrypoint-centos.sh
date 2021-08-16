#!/bin/bash

set -ex

install_ref="${PKG_INSTALL_REF}"

if [ -z "${install_ref}" ]; then
    echo ::error "Cannot determine package install ref."
    exit 1
fi

dist='el$releasever'
if [ -n "${PKG_SUBDIST}" ]; then
    dist+=".${PKG_SUBDIST}"
fi

cat <<EOF >/etc/yum.repos.d/edgedb.repo
[edgedb]
name=edgedb
baseurl=https://packages.edgedb.com/rpm/${dist}/
enabled=1
gpgcheck=1
gpgkey=https://packages.edgedb.com/keys/edgedb.asc
EOF

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

try=1
while [ $try -le 30 ]; do
    yum makecache && yum install --verbose -y "${install_ref}" && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

edgedb-server-${slot} --help
edgedb --help
