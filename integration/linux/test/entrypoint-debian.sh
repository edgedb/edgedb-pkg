#!/bin/bash

set -ex

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

dist="${PKG_PLATFORM_VERSION}"

export DEBIAN_FRONTEND="noninteractive"

apt-get update
apt-get install -y curl gnupg apt-transport-https jq

mkdir -p /usr/local/share/keyrings
curl --proto '=https' --tlsv1.2 -sSf \
    -o /usr/local/share/keyrings/edgedb-keyring.gpg \
    https://packages.edgedb.com/keys/edgedb-keyring.gpg
echo deb [signed-by=/usr/local/share/keyrings/edgedb-keyring.gpg] \
    https://packages.edgedb.com/apt "${dist}" main \
    > /etc/apt/sources.list.d/edgedb.list
if [ -n "${PKG_SUBDIST}" ]; then
    echo deb [signed-by=/usr/local/share/keyrings/edgedb-keyring.gpg] \
        https://packages.edgedb.com/apt "${dist}" "${PKG_SUBDIST}" \
        > /etc/apt/sources.list.d/edgedb.list
fi

try=1
while [ $try -le 30 ]; do
    apt-get update && apt-get install -y edgedb-cli && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

slot=
deb=
for pack in ${dest}/*.tar; do
    if [ -e "${pack}" ]; then
        slot=$(tar -xOf "${pack}" "build-metadata.json" \
               | jq -r ".version_slot")
        deb=$(tar -xOf "${pack}" "build-metadata.json" \
              | jq -r ".contents | keys[]" \
              | grep "^edgedb-server.*\\.deb$")
        if [ -n "${deb}" ]; then
            break
        fi
    fi
done

if [ -z "${deb}" ]; then
    echo "${dest} does not seem to contain an edgedb-server .deb" >&2
    exit 1
fi

if [ -z "${slot}" ]; then
    echo "could not determine version slot from build metadata" >&2
    exit 1
fi

machine=$(uname -m)
tmpdir=$(mktemp -d)
tar -x -C "${tmpdir}" -f "${pack}" "${deb}"
apt-get install -y "${tmpdir}/${deb}"
rm -rf "${tmpdir}"

edgedb-server-${slot} --version

if [ "$1" == "bash" ]; then
    echo su edgedb -c \
        "/usr/lib/${machine}-linux-gnu/edgedb-server-${slot}/bin/python3 \
         -m edb.tools --no-devmode test \
         /usr/share/edgedb-server-${slot}/tests \
         -e cqa_ -e tools_ \
         --verbose"
    exec "$@"
else
    if [ -n "${PKG_TEST_JOBS}" ]; then
        dash_j="-j${PKG_TEST_JOBS}"
    else
        dash_j=""
    fi
    su edgedb -c \
        "/usr/lib/${machine}-linux-gnu/edgedb-server-${slot}/bin/python3 \
         -m edb.tools --no-devmode test \
         /usr/share/edgedb-server-${slot}/tests \
         -e cqa_ -e tools_ \
         --verbose ${dash_j}"
    echo "Success!"
fi
