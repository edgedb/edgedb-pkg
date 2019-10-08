#!/bin/bash

set -e

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.edgedb.com
    Port 2224
    StrictHostKeyChecking no
EOF

set -ex

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

cat <<EOF >"/tmp/sftp-batch"
put ${dest}/*.pkg incoming/macos/
EOF

sftp -b /tmp/sftp-batch uploader@upload-packages.edgedb.com
