#!/bin/bash

set -e

HOME=$(getent passwd "$(whoami)" | cut -d: -f6)
: ${PACKAGE_SERVER:=upload-packages.edgedb.com}

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
if [ -f "${PACKAGE_UPLOAD_SSH_KEY_FILE}" ]; then
    cp "${PACKAGE_UPLOAD_SSH_KEY_FILE}" "${HOME}/.ssh/id_ed25519"
else
    echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
fi
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

cat <<EOF >"${HOME}/.ssh/config"
Host ${PACKAGE_SERVER}
    User uploader
    Port 2222
    StrictHostKeyChecking no
EOF

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

dest="artifacts"
key=""
if [ -n "${PKG_PLATFORM}" ]; then
    key+="-${PKG_PLATFORM}"
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    key+="-${PKG_PLATFORM_VERSION}"
    dest+="-${PKG_PLATFORM_VERSION}"
fi

cd "${dest}"
list=$(mktemp)
batch=$(mktemp)
find . -type f -printf '%P\n' > "${list}"
chmod g+rw "${list}"

cat <<EOF >${batch}
put -r * incoming/
put -p ${list} incoming/triggers/
EOF

sftp -b "${batch}" uploader@"$PACKAGE_SERVER"

rm "${list}" "${batch}"
