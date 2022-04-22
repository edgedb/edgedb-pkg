#!/bin/bash

set -Exeo pipefail

extraopts=
if [ -n "${SRC_REF}" ]; then
    extraopts+=" --source-ref=${SRC_REF}"
fi

if [ -n "${BUILD_IS_RELEASE}" ]; then
    extraopts+=" --release"
fi

if [ -n "${PKG_REVISION}" ]; then
    if [ "${PKG_REVISION}" = "<current-date>" ]; then
        PKG_REVISION="$(date -u +%Y%m%d%H%M)"
    fi
    extraopts+=" --pkg-revision=${PKG_REVISION}"
fi

if [ -n "${PKG_SUBDIST}" ]; then
    extraopts+=" --pkg-subdist=${PKG_SUBDIST}"
fi

if [ -n "${EXTRA_OPTIMIZATIONS}" ]; then
    extraopts+=" --extra-optimizations"
fi

if [ -n "${BUILD_GENERIC}" ]; then
    extraopts+=" --generic"
fi

if [ -n "${PKG_BUILD_JOBS}" ]; then
    extraopts+=" --jobs=${PKG_BUILD_JOBS}"
fi

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi

if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

if [ -z "${PACKAGE}" ]; then
    PACKAGE="edgedbpkg.edgedb:EdgeDB"
fi

echo python3 -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"

pip3 install -U git+https://github.com/edgedb/edgedb-pkg

python3 -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"

ls -al "${dest}"
