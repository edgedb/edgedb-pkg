#!/bin/bash

set -ex

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.deb"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"
echo "SLOT=$slot"

apt-get update
apt install -y ./"${dest}"/edgedb-common_*_amd64.deb \
               ./"${dest}"/edgedb-${slot}_*_amd64.deb
su edgedb -c "/usr/lib/x86_64-linux-gnu/edgedb-${slot}/bin/python3 \
              -m edb.tools --no-devmode test /usr/share/edgedb-${slot}/tests \
              -e cqa_ --output-format=simple"
echo "Success!"
