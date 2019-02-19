#!/bin/bash

set -ex

cat <<EOF >/etc/yum.repos.d/edgedb.repo
[edgedb]
name=edgedb
baseurl=https://packages.prod.edgedatabase.net/rpm/el7/
enabled=1
gpgcheck=1
gpgkey=https://packages.prod.edgedatabase.net/keys/edgedb.asc
EOF

yum install -y edgedb-0
edgedb --help
