#!/bin/bash

set -Exeo pipefail

pip install -U git+https://github.com/edgedb/edgedb-pkg

# Circumvent a dubious practice of Windows intercepting
# bare invocations of "bash" to mean "WSL", since make
# runs its shells using bare names even if SHELL contains
# a fully-qualified path.
shell_path=$(mktemp -d)
cp -a "${SHELL}" "${shell_path}/realbash"
export PATH="${shell_path}:${PATH}"

extraopts=
if [ -n "${SRC_REF}" ]; then
    extraopts+=" --source-ref=${SRC_REF}"
fi

if [ -n "${BUILD_IS_RELEASE}" ]; then
    extraopts+=" --release"
fi

if [ -n "${DEBUG_SYMBOLS}" ]; then
    extraopts+=" --build-debug"
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

if [ -n "${PKG_TAGS}" ]; then
    extraopts+=" --pkg-tags=${PKG_TAGS}"
fi

if [ -n "${PKG_COMPRESSION}" ]; then
    extraopts+=" --pkg-compression=${PKG_COMPRESSION}"
fi

if [ -n "${BUILD_GENERIC}" ]; then
    extraopts+=" --generic"
fi

if [ -n "${PKG_PLATFORM_ARCH}" ]; then
    extraopts+=" --arch=${PKG_PLATFORM_ARCH}"
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

python -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"

ls -al "${dest}"
