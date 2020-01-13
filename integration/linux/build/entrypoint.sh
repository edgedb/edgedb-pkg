#!/bin/bash

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

set -Exeo pipefail

pip install -U git+https://github.com/edgedb/metapkg
pip install -U git+https://github.com/edgedb/edgedb-pkg

if [ -n "${METAPKG_PATH}" ]; then
    p=$(python -c 'import metapkg;print(metapkg.__path__[0])')
    rm -rf "${p}"
    cp -a "${METAPKG_PATH}" "${p}"
    ls -al "${p}"
fi

extraopts=
if [ -n "${SRC_REVISION}" ]; then
    extraopts+=" --source-revision=${SRC_REVISION}"
fi

if [ -n "${PKG_REVISION}" ]; then
    if [ "${PKG_REVISION}" = "<current-date>" ]; then
        PKG_REVISION="$(date --utc +%Y%m%d%H)"
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

python -m metapkg build --dest="${dest}" ${extraopts} edgedbpkg.edgedb:EdgeDB

ls -al "${dest}"
