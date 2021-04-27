#!/bin/bash

set -Exeo pipefail

pip install -U git+https://github.com/edgedb/metapkg
pip install -U git+https://github.com/edgedb/edgedb-pkg

# Circumvent a dubious practice of Windows intercepting
# bare invocations of "bash" to mean "WSL", since make
# runs its shells using bare names even if SHELL contains
# a fully-qualified path.
shell_path=$(dirname "${SHELL}")
cp -a "${SHELL}" "${shell_path}/realbash"

extraopts=
if [ -n "${SRC_REF}" ]; then
    extraopts+=" --source-ref=${SRC_REF}"
fi

if [ -n "${PKG_VERSION}" ]; then
    extraopts+=" --pkg-version=${PKG_VERSION}"
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

python -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"

ls -al "${dest}"
