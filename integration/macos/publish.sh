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
key=""
if [ -n "${PKG_PLATFORM}" ]; then
    key+="-${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    key+="-${PKG_PLATFORM_VERSION}"
fi

cd "${dest}"
list=$(mktemp)
batch=$(mktemp)
find . -type f > "${list}"

cat <<EOF >${batch}
put -r * ./incoming/
put ${list} ./incoming/triggers/upload${key}.list
EOF

sftp -b "${batch}" uploader@upload-packages.edgedb.com
rm "${list}" "${batch}"
