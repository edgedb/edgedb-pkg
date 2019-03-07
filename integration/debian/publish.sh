#!/bin/bash

set -e

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${DPUT_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.edgedb.com
    Port 2222
    StrictHostKeyChecking no
EOF

set -ex

cat <<EOF >/tmp/dput.cf
[edgedb-prod]
fqdn                    = upload-packages.edgedb.com
incoming                = /incoming
login                   = uploader
allow_dcut              = 1
method                  = sftp
allow_unsigned_uploads  = 1
EOF

dput -d -d -c /tmp/dput.cf edgedb-prod artifacts/*.changes
