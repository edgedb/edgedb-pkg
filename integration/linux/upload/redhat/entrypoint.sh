#!/bin/bash

set -e

HOME=$(getent passwd "$(whoami)" | cut -d: -f6)

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.edgedb.com
    User uploader
    Port 2223
    StrictHostKeyChecking no
EOF

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
ls *.rpm > "upload${key}.list"

cat <<EOF >/tmp/sftp-batch
put *.rpm ./incoming/
put upload${key}.list ./incoming/triggers/
EOF

sftp -b /tmp/sftp-batch uploader@upload-packages.edgedb.com
