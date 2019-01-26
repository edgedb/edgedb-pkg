#!/bin/bash

set -ex

apt-get update
dpkg -i artifacts/edgedb-server_*_amd64.deb || apt-get -f install -y
su edgedb -c '/usr/lib/x86_64-linux-gnu/edgedb-server/bin/python3 \
              -m edb.tools --no-devmode test /usr/share/edgedb-server/tests \
              --output-format=simple'
systemctl enable --now edgedb-0
"[[ $(echo 'SELECT 1 + 3;' | edgedb -u edgedb) == *4* ]]"
