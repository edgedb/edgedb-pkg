#!/bin/bash

set -e

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.edgedb.com
    Port 2223
    StrictHostKeyChecking no
EOF

cd artifacts
ls *.rpm > upload.list

cat <<EOF >"/tmp/sftp-batch"
put *.rpm incoming/
put upload.list incoming/triggers/
EOF

sftp -b /tmp/sftp-batch uploader@upload-packages.edgedb.com
