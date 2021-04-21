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

cat <<EOF >>"${HOME}/.ssh/config"
Host ${PACKAGE_SERVER}
    User uploader
    Port 2223
    StrictHostKeyChecking no
EOF

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

cat <<EOF >/tmp/dput.cf
[edgedb-prod]
fqdn                    = ${PACKAGE_SERVER}
incoming                = /incoming
login                   = uploader
allow_dcut              = 1
method                  = sftp
allow_unsigned_uploads  = 1
EOF

dput -d -d -c /tmp/dput.cf edgedb-prod "${dest}"/*.changes
