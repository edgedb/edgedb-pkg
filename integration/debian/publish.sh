#!/bin/bash

set -e

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${DPUT_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

cat <<EOF >"${HOME}/.ssh/config"
Host upload-packages.prod.edgedatabase.net
    Port 2222
    StrictHostKeyChecking no
EOF

set -ex

cat <<EOF >/tmp/dput.cf
[edgedb-prod]
fqdn                    = upload-packages.prod.edgedatabase.net
incoming                = /incoming
login                   = uploader
allow_dcut              = 1
method                  = sftp
allow_unsigned_uploads  = 1
EOF

dput -d -d -c /tmp/dput.cf edgedb-prod artifacts/*.changes
# Do not use the post_upload_command since that seems to ignore
# erroneous exit.
ssh reprepro@upload-packages.prod.edgedatabase.net \
    /usr/bin/reprepro processincoming main
