#!/bin/bash

set -Exeo pipefail

pip3 install -U git+https://github.com/edgedb/metapkg
pip3 install -U git+https://github.com/edgedb/edgedb-pkg

extraopts=
if [ -n "${SRC_REF}" ]; then
    extraopts+=" --source-ref=${SRC_REF}"
fi

if [ -n "${PKG_VERSION}" ]; then
    extraopts+=" --pkg-version=${PKG_VERSION}"
fi

if [ -n "${PKG_REVISION}" ]; then
    if [ "${PKG_REVISION}" = "<current-date>" ]; then
        PKG_REVISION="$(date -u +%Y%m%d%H)"
    fi
    extraopts+=" --pkg-revision=${PKG_REVISION}"
fi

if [ -n "${PKG_SUBDIST}" ]; then
    extraopts+=" --pkg-subdist=${PKG_SUBDIST}"
fi

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

python3 -m metapkg build --dest="${dest}" ${extraopts} edgedbpkg.edgedb:EdgeDB

ls -al "${dest}"
