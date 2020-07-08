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

re="edgedb-server-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.deb"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"
echo "SLOT=$slot"

dist="${PKG_PLATFORM_VERSION}"
if [ -n "${PKG_SUBDIST}" ]; then
    dist+=".${PKG_SUBDIST}"
fi

apt-get update
apt-get install -y curl gnupg apt-transport-https
curl https://packages.edgedb.com/keys/edgedb.asc | apt-key add -
echo deb [arch=amd64] https://packages.edgedb.com/apt ${dist} main \
    >> /etc/apt/sources.list.d/edgedb.list

try=1
while [ $try -le 30 ]; do
    apt-get update && apt-get install -y edgedb-cli && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

apt-get install -y ./"${dest}"/edgedb-server-${slot}_*_amd64.deb
su edgedb -c "/usr/lib/x86_64-linux-gnu/edgedb-server-${slot}/bin/python3 \
              -m edb.tools --no-devmode test \
              /usr/share/edgedb-server-${slot}/tests \
              -e cqa_ -e tools_ --output-format=simple"
echo "Success!"
