#!/bin/bash

set -Exeo pipefail
shopt -s nullglob

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

if [ -z "${VIRTUAL_ENV}"]; then
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -U pip setuptools wheel
fi

python3 -m pip install --upgrade --upgrade-strategy=eager \
    git+https://github.com/edgedb/edgedb-pkg

for old in "${dest}"/*.tar; do
    rm -f "${old}"
done

echo python3 -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"
python3 -m metapkg build -vvv --dest="${dest}" ${extraopts} "${PACKAGE}"

ls -al "${dest}"
