#!/bin/bash

set -Exeo pipefail

pip install -U git+https://github.com/edgedb/metapkg
pip install -U git+https://github.com/edgedb/edgedb-pkg

if [ -n "${METAPKG_PATH}" ]; then
    p=$(python -c 'import metapkg;print(metapkg.__path__[0])')
    rm -rf "${p}"
    ln -s "${METAPKG_PATH}" "${p}"
    ls -al "${p}"
fi

extraopts=
if [ -n "${SRC_REF}" ]; then
    extraopts+=" --source-ref=${SRC_REF}"
fi

if [ -n "${PKG_VERSION}" ]; then
    extraopts+=" --pkg-version=${PKG_VERSION}"
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

if [ -n "${EXTRA_OPTIMIZATIONS}" ]; then
    extraopts+=" --extra-optimizations"
fi

if [ -n "${BUILD_GENERIC}" ]; then
    extraopts+=" --generic"
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

if [ "$1" == "bash" ]; then
    echo python -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"
    exec /bin/bash
else
    python -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"
    ls -al "${dest}"
fi
