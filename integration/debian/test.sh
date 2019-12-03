#!/bin/bash

set -ex

re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.deb"
slot="$(ls artifacts | sed -n -E "s/${re}/\1/p")"

apt-get update
apt install -y ./artifacts/edgedb-common_*_amd64.deb \
               ./artifacts/edgedb-${slot}_*_amd64.deb
systemctl enable --now edgedb-${slot} || \
  (journalctl -u edgedb-${slot} && exit 1)
su edgedb -c 'echo "test" | \
              edgedb --admin alter role edgedb --password-from-stdin'
su edgedb -c "/usr/lib/x86_64-linux-gnu/edgedb-${slot}/bin/python3 \
              -m edb.tools --no-devmode test /usr/share/edgedb-${slot}/tests \
              -e cqa_ -e tools_ --output-format=simple"
su edgedb -c 'echo "test" | \
              edgedb --admin configure insert auth \
                --method=trust --priority=0'
[[ "$(echo 'SELECT 1 + 3;' | edgedb -u edgedb)" == *4* ]] || exit 1
echo "Success!"
