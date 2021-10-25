#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

install_ref="${PKG_INSTALL_REF}"

if [ -z "${install_ref}" ]; then
    echo ::error "Cannot determine package install ref."
    exit 1
fi

dist="${PKG_PLATFORM}-${PKG_PLATFORM_VERSION}"
if [ -n "${PKG_SUBDIST}" ]; then
    dist+=".${PKG_SUBDIST}"
fi

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

url="https://packages.edgedb.com/archive/${dist}/${install_ref}"

try=1
while [ $try -le 30 ]; do
    wget --secure-protocol=PFS --https-only "${url}" && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

artifact=$(basename "${install_ref}")
if ! [ -e "${artifact}" ]; then
    echo ::error "Downloaded something, but `${artifact}` does not exist."
    exit 1
fi

tdir="edgedb-server-extracted"
mkdir -p "$tdir"

case "${artifact}" in
    *.tar.gz)
        tar -f "${artifact}" -C "$tdir" -xz --strip-components=1
        ;;
    *.tar.zst)
        tar -f "${artifact}" -C "$tdir" -x --zstd --strip-components=1
        ;;
    *)
        echo ::error "Unrecognized archive: ${archive}"
        exit 1
        ;;
esac

"${tdir}/bin/edgedb-server" --version
"${tdir}/bin/edgedb-server" --help
