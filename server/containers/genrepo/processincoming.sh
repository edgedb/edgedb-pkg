#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <pkg-file>" >&2
    exit 1
fi

pkg=$1
dist=$(basename $(dirname $pkg))

case "${dist}" in
    macos)
        ;;
    source)
        ;;
    *)
        echo "Unsupported dist: ${dist}" >&2; exit 1 ;;
esac

if [ ! -e /var/lib/repos/${dist} ]; then
    mkdir /var/lib/repos/${dist}
fi

mkdir -p /tmp/repo-staging/

filename=$(basename "${pkg}")
mv "${pkg}" /tmp/repo-staging
gpg --detach-sign --armor "/tmp/repo-staging/${filename}"
mv "/tmp/repo-staging/${filename}*" "/var/lib/repos/${dist}"
