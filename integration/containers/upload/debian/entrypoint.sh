#!/bin/bash

set -e

HOME=$(getent passwd "$(whoami)" | cut -d: -f6)

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

cat <<EOF >>"${HOME}/.ssh/config"
Host upload-packages.edgedb.com
    User uploader
    Port 2222
    StrictHostKeyChecking no
EOF

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

cat <<EOF >/tmp/dput.cf
[edgedb-prod]
fqdn                    = upload-packages.edgedb.com
incoming                = /incoming
login                   = uploader
allow_dcut              = 1
method                  = sftp
allow_unsigned_uploads  = 1
EOF

dput -d -d -c /tmp/dput.cf edgedb-prod "${dest}"/*.changes
