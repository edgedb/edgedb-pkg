#!/bin/sh

set -ex

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest="${dest}/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest="${dest}-${PKG_PLATFORM_VERSION}"
fi
if [ -n "${PKG_TEST_JOBS}" ]; then
    dash_j="-j${PKG_TEST_JOBS}"
else
    dash_j=""
fi

wget "https://packages.edgedb.com/dist/linux-x86_64/edgedb-cli_latest" \
    -O /bin/edgedb
chmod +x /bin/edgedb

cat "${dest}/package-version.json"
tarball="${dest}/$(cat "${dest}/package-version.json" | jq -r .installref)"
mkdir /edgedb
chmod 1777 /tmp
tar -xzf "${tarball}" --strip-components=1 -C "/edgedb/"
touch /etc/group
addgroup edgedb
touch /etc/passwd
adduser -G edgedb -H -D edgedb

if [ "$1" == "bash" ]; then
    exec /bin/sh
fi

exec gosu edgedb:edgedb /edgedb/bin/python3 \
    -m edb.tools --no-devmode test \
    /edgedb/data/tests \
    -e cqa_ -e tools_ \
    --verbose ${dash_j}
