#!/bin/bash

set -ex

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

re="edgedb-server-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.rpm"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"

yum install -y "${dest}"/edgedb-server-common*.x86_64.rpm \
               "${dest}"/edgedb-server-${slot}*.x86_64.rpm
su edgedb -c "/usr/lib64/edgedb-server-${slot}/bin/python3 \
              -m edb.tools --no-devmode test \
              /usr/share/edgedb-server-${slot}/tests \
              -e cqa_ -e tools_ --output-format=simple"
echo "Success!"
