#!/bin/bash

set -Exeo pipefail

: "${CARGO_HOME:=$HOME/.cargo}"
: "${PYTHON:=python}"

mkdir -p ~/.cache/cargo/{git,registry}
mkdir -p "$CARGO_HOME"
rm -rf "${CARGO_HOME}"/{git,registry}
ln -s ~/.cache/cargo/registry "${CARGO_HOME}/registry"
ln -s ~/.cache/cargo/git "${CARGO_HOME}/git"

extraopts=
if [ -n "${SRC_REF}" ]; then
    extraopts+=" --source-ref=${SRC_REF}"
fi

if [ -n "${BUILD_IS_RELEASE}" ]; then
    extraopts+=" --release"
fi

if [ -n "${PKG_REVISION}" ]; then
    if [ "${PKG_REVISION}" = "<current-date>" ]; then
        PKG_REVISION="$(date --utc +%Y%m%d%H%M)"
    fi
    extraopts+=" --pkg-revision=${PKG_REVISION}"
fi

if [ -n "${PKG_SUBDIST}" ]; then
    extraopts+=" --pkg-subdist=${PKG_SUBDIST}"
fi

if [ -n "${PKG_TAGS}" ]; then
    extraopts+=" --pkg-tags=${PKG_TAGS}"
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
if [ -n "${PKG_PLATFORM_LIBC}" ]; then
    dest+="${PKG_PLATFORM_LIBC}"
    extraopts+=" --libc=${PKG_PLATFORM_LIBC}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi
if [ -n "${PKG_PLATFORM_ARCH}" ]; then
    extraopts+=" --arch=${PKG_PLATFORM_ARCH}"
fi

if [ -z "${PACKAGE}" ]; then
    PACKAGE="edgedbpkg.edgedb:EdgeDB"
fi

if [ -z "${VIRTUAL_ENV}"]; then
    mkdir -p "/var/lib/metapkg/venv"
    ${PYTHON} -m venv "/var/lib/metapkg/venv"
    source "/var/lib/metapkg/venv/bin/activate"
    PYTHON="python"
    ${PYTHON} -m pip install -U pip setuptools wheel
fi

${PYTHON} -m pip install -U meson
${PYTHON} -m pip install -U git+https://github.com/edgedb/edgedb-pkg

if [ -n "${METAPKG_PATH}" ]; then
    p=$(${PYTHON} -c 'import metapkg;print(metapkg.__path__[0])')
    rm -rf "${p}"
    ln -s "${METAPKG_PATH}" "${p}"
    ls -al "${p}"
fi

if [ "$1" == "bash" ] || [ "${GET_SHELL}" == "true" ]; then
    echo ${PYTHON} -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"
    exec /bin/bash
else
    ${PYTHON} -m metapkg build -vvv --dest="${dest}" ${extraopts} "${PACKAGE}"
    ls -al "${dest}"
fi
