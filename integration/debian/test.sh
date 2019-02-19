#!/bin/bash

set -ex

apt-get update
dpkg -i artifacts/edgedb-0_*_amd64.deb || apt-get -f install -y
su edgedb -c '/usr/lib/x86_64-linux-gnu/edgedb-0/bin/python3 \
             -m edb.tools --no-devmode test /usr/share/edgedb-0/tests \
             -e flake8 --output-format=simple'
systemctl enable --now edgedb-0
[[ "$(echo 'SELECT 1 + 3;' | edgedb -u edgedb)" == *4* ]]
echo "Success!"
