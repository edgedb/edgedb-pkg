#!/bin/bash

set -ex

cat <<'EOF' >/etc/yum.repos.d/edgedb.repo
[edgedb]
name=edgedb
baseurl=https://packages.edgedb.com/rpm/el$releasever/
enabled=1
gpgcheck=1
gpgkey=https://packages.edgedb.com/keys/edgedb.asc
EOF

yum install -y edgedb-1-alpha1
edgedb --help
