#!/bin/bash

set -ex

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.pkg"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"
fwpath="/Library/Frameworks/EdgeDB.framework/"

sudo installer -dumplog -verbose \
    -pkg "${dest}"/*.pkg \
    -target / || (sudo cat /var/log/install.log && exit 1)

socket="/var/run/edgedb/.s.EDGEDB.5656"

try=1
while [ $try -le 10 ]; do
    [ -e "${socket}" ] && break
    try=$(( $try + 1 ))
    sleep 1
done

sudo launchctl print system/com.edgedb.edgedb-"${slot}"

if [ ! -e "${socket}" ]; then
    echo "Server did not start within 10 seconds."
    exit 1
fi

source /etc/profile

sudo su edgedb -c \
    'echo "test" | edgedb --admin alter role edgedb --password-from-stdin'

sudo su edgedb -c \
    "${fwpath}/Versions/${slot}/lib/edgedb-${slot}/bin/python3 \
     -m edb.tools --no-devmode test \
     ${fwpath}/Versions/${slot}/share/edgedb-${slot}/tests \
     -e cqa_ -e tools_ --output-format=simple"

sudo su edgedb -c \
    'edgedb --admin configure insert auth --method=trust --priority=0'

[[ "$(echo 'SELECT 1 + 3;' | edgedb -u edgedb)" == *4* ]] || exit 1

echo "Success!"
