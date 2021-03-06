#!/bin/bash

set -e

HOME=$(getent passwd "$(whoami)" | cut -d: -f6)

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
if [ -f "${PACKAGE_UPLOAD_SSH_KEY_FILE}" ]; then
    cp "${PACKAGE_UPLOAD_SSH_KEY_FILE}" "${HOME}/.ssh/id_ed25519"
else
    echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
fi
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.edgedb.com
    User uploader
    Port 2224
    StrictHostKeyChecking no
EOF

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

dest="artifacts"
key=""
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
    key+="-${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
    key+="-${PKG_PLATFORM_VERSION}"
fi

cd "${dest}"
ls -1 *.rpm > "upload${key}.list"
chmod g+rw "upload${key}.list"

cat <<EOF >/tmp/sftp-batch
put *.rpm ./incoming/
put upload${key}.list ./incoming/triggers/
EOF

sftp -b /tmp/sftp-batch uploader@upload-packages.edgedb.com
