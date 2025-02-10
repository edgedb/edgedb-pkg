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
    > "/etc/apt/sources.list.d/edgedb.list"
if [ -n "${PKG_SUBDIST}" ]; then
    echo deb [signed-by=/usr/local/share/keyrings/edgedb-keyring.gpg] \
        https://packages.edgedb.com/apt "${dist}" "${PKG_SUBDIST}" \
        > "/etc/apt/sources.list.d/edgedb-${PKG_SUBDIST}.list"
fi

try=1
while [ $try -le 30 ]; do
    apt-get update && apt-get install -y edgedb-cli && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})" >&2
    sleep 10
done

if ! type edgedb >/dev/null; then
    echo "could not install edgedb-cli" >&2
    exit $s
fi

slot=
deb=
for pack in ${dest}/*.tar; do
    if [ -e "${pack}" ]; then
        slot=$(tar -xOf "${pack}" "build-metadata.json" \
               | jq -r ".version_slot")
        deb=$(tar -xOf "${pack}" "build-metadata.json" \
              | jq -r ".contents | keys[]" \
              | grep "^gel-server.*\\.deb$" \
              || true)
        if [ -n "${deb}" ]; then
            break
        fi
        deb=$(tar -xOf "${pack}" "build-metadata.json" \
              | jq -r ".contents | keys[]" \
              | grep "^edgedb-server.*\\.deb$" \
              || true)
        if [ -n "${deb}" ]; then
            break
        fi
    fi
done

if [ -z "${deb}" ]; then
    echo "${dest} does not seem to contain an {edgedb|gel}-server .deb" >&2
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

if [[ $deb == *gel-server* ]]; then
    user="gel"
    server="gel-server-${slot}"
else
    user="edgedb"
    server="edgedb-server-${slot}"
fi

"$server" --version

if [ -n "${PKG_TEST_JOBS}" ]; then
    dash_j="-j${PKG_TEST_JOBS}"
else
    dash_j=""
fi

cmd="/usr/lib/${machine}-linux-gnu/${server}/bin/python3 \
     -m edb.tools --no-devmode test \
     /usr/share/${server}/tests \
     -e cqa_ -e tools_ \
     --verbose ${dash_j}"

if [ "$1" == "bash" ]; then
    echo su "$user" -c "$cmd"
    exec /bin/bash
else
    su "$user" -c "$cmd"
    echo "Success!"
fi
