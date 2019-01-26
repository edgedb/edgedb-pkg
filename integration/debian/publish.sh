#!/bin/bash

set -e

mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"
echo "${DPUT_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"
chmod 400 "${HOME}/.ssh/id_ed25519"

set -ex

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y dput

dput -d -d artifacts/*.changes \
    --override "fqdn=upload-packages.prod.edgedatabase.net:2222" \
    --override "method=sftp" \
    --override "full_upload_log=true" \
    --override "incoming=/data/apt/incoming/" \
    --override "login=root" \
    --override "allow_unsigned_uploads=true" \
    --override 'post_upload_command="ssh -p2222 root@upload-packages.prod.edgedatabase.net -- reprepro --verbose processincoming"'
