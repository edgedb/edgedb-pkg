#!/bin/bash

set -ex

slot="${PKG_VERSION_SLOT}"

if [ -z "${slot}" ]; then
    echo ::error "Cannot determine package version slot."
    exit 1
fi

dist='el\\$releasever'
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

yum install -y edgedb-${slot}
edgedb --help