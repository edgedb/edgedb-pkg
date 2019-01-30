#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <rpm-file>" >&2
    exit 1
fi

pkg=$1
release=$(rpm -qp --queryformat '%{RELEASE}' "${pkg}")
dist=${release##*.}

case "${dist}" in
    el7)
        ;;
    *)
        echo "Unsupported dist: ${dist}" >&2; exit 1 ;;
esac

if [ ! -e /var/lib/repos/${dist} ]; then
    mkdir /var/lib/repos/${dist}
    createrepo --database /var/lib/repos/${dist}
fi

mkdir -p /tmp/repo-staging/

filename=$(basename "${pkg}")
mv "${pkg}" /tmp/repo-staging
rpm --resign "/tmp/repo-staging/${filename}"
mv "/tmp/repo-staging/${filename}" "/var/lib/repos/${dist}"
createrepo --update "/var/lib/repos/${dist}"
gpg --detach-sign --armor "/var/lib/repos/${dist}/repodata/repomd.xml"
