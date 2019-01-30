#!/bin/bash

set -ex

rpm --import https://packages.prod.edgedatabase.net/keys/edgedb.asc
echo <<EOF >/etc/yum.repos.d/
[edgedb]
name=edgedb
baseurl=https://packages.prod.edgedatabase.net/rpm/el7/
enabled=1
gpgcheck=1
gpgkey=https://packages.prod.edgedatabase.net/keys/edgedb.asc
EOF

yum install -y edgedb-server
edgedb-server --help
edgedb --help
