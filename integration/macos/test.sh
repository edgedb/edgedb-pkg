#!/bin/bash

set -ex

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

re="edgedb-server-([[:digit:]]+(-(alpha|beta|rc)[[:digit:]]+)?(-dev[[:digit:]]+)?).*\.pkg"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"
fwpath="/Library/Frameworks/EdgeDB.framework/"
python="${fwpath}/Versions/${slot}/lib/edgedb-server-${slot}/bin/python3"

# Install the CLI tools.
dist=""
if [ -n "${PKG_PLATFORM}" ]; then
    dist+="${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dist+="-${PKG_PLATFORM_VERSION}"
fi
if [ -n "${PKG_SUBDIST}" ]; then
    dist+=".${PKG_SUBDIST}"
fi

clipath="edgedb-cli_latest"
if [ -n "${PKG_SUBDIST}" ]; then
    clipath="${clipath}_${PKG_SUBDIST}"
fi

curl -fL "https://packages.edgedb.com/dist/${dist}/${clipath}" > edgedb-cli

sudo mkdir -p /usr/local/bin
sudo cp edgedb-cli /usr/local/bin/edgedb
sudo chmod +x /usr/local/bin/edgedb

sudo installer -dumplog -verbose \
    -pkg "${dest}"/*.pkg \
    -target / || (sudo tail -300 /var/log/install.log && exit 1)

set +e
source /etc/profile
set -e

sudo su edgedb -c \
    "${python} -m edb.tools --no-devmode test \
     ${fwpath}/Versions/${slot}/share/edgedb-server-${slot}/tests \
     -e cqa_ -e tools_ --verbose"

echo "Success!"
