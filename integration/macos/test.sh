#!/bin/bash

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

dlurl="https://packages.edgedb.com/dist/${PKG_PLATFORM_VERSION}-apple-darwin"

sudo curl -fL "${dlurl}/edgedb-cli" -o /usr/local/bin/edgedb
sudo chmod +x /usr/local/bin/edgedb

tarball=
for pack in ${dest}/*.tar; do
    if [ -e "${pack}" ]; then
        tarball=$(tar -xOf "${pack}" "build-metadata.json" \
                  | jq -r ".installrefs[]" \
                  | grep ".tar.gz$")
        if [ -n "${tarball}" ]; then
            break
        fi
    fi
done

if [ -z "${tarball}" ]; then
    echo "${dest} does not contain a valid build tarball" >&2
    exit 1
fi

mkdir edgedb
gtar -xOf "${pack}" "${tarball}" | gtar -xzf- --strip-components=1 -C edgedb

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

./edgedb/bin/python3 \
    -m edb.tools --no-devmode test \
    ./edgedb/data/tests \
    -e cqa_ -e tools_ \
    --verbose ${dash_j}
