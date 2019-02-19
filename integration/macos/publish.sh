#!/bin/bash

set -e

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${DPUT_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.prod.edgedatabase.net
    Port 2224
    StrictHostKeyChecking no
EOF

set -ex

cat <<EOF >"/tmp/sftp-batch"
put artifacts/*.pkg incoming/macos/
EOF

sftp -b /tmp/sftp-batch uploader@upload-packages.prod.edgedatabase.net
