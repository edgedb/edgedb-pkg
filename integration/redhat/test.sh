#!/bin/bash

set -ex

re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.rpm"
slot="$(ls artifacts | sed -n -E "s/${re}/\1/p")"

yum install -y artifacts/edgedb-common*.x86_64.rpm \
               artifacts/edgedb-${slot}*.x86_64.rpm
systemctl enable --now edgedb-${slot} || \
  (journalctl -u edgedb-${slot} && exit 1)
su edgedb -c 'echo "test" | \
              edgedb --admin alter role edgedb --password-from-stdin'
su edgedb -c "/usr/lib64/edgedb-${slot}/bin/python3 \
              -m edb.tools --no-devmode test /usr/share/edgedb-${slot}/tests \
              -e flake8 --output-format=simple"
su edgedb -c 'echo "test" | \
              edgedb --admin configure insert auth \
                --method=trust --priority=0'
[[ "$(echo 'SELECT 1 + 3;' | edgedb -u edgedb)" == *4* ]] || exit 1
echo "Success!"
