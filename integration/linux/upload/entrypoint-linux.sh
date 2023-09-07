#!/bin/bash

set -e

HOME=$(getent passwd "$(whoami)" | cut -d: -f6)
: ${PACKAGE_SERVER:="sftp://uploader@package-upload.edgedb.net/"}

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
if [ -f "${PACKAGE_UPLOAD_SSH_KEY_FILE}" ]; then
    cp "${PACKAGE_UPLOAD_SSH_KEY_FILE}" "${HOME}/.ssh/id_ed25519"
else
    echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
fi
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_LIBC}" ]; then
    dest+="${PKG_PLATFORM_LIBC}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
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

sftp -o StrictHostKeyChecking=no -b "$batch" "$PACKAGE_SERVER"

rm "$list" "$batch"
