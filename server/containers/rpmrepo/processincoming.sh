#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <upload-list>" >&2
    exit 1
fi

list=$1
dir="%%REPO_INCOMING_DIR%%"

while read -r -u 10 pkgname; do

    pkg="${dir}/${pkgname}"
    release=$(rpm -qp --queryformat '%{RELEASE}' "${pkg}")
    dist=${release##*.}
    releaseno=${release%.*}
    subdist=${releaseno##*.}
    if [ -n "${subdist}" ]; then
        dist="${dist}-${subdist}"
    fi

    case "${dist}" in
        el7*)
            ;;
        *)
            echo "Unsupported dist: ${dist}" >&2; exit 1 ;;
    esac

    if [ ! -e /var/lib/repos/${dist} ]; then
        mkdir /var/lib/repos/${dist}
        createrepo --database /var/lib/repos/${dist}
    fi

    mkdir -p /tmp/repo-staging/

    mv "${pkg}" /tmp/repo-staging
    echo | rpm --resign "/tmp/repo-staging/${pkgname}"
    mv "/tmp/repo-staging/${pkgname}" "/var/lib/repos/${dist}"
    createrepo --update "/var/lib/repos/${dist}"
    gpg --yes --batch --detach-sign --armor \
        "/var/lib/repos/${dist}/repodata/repomd.xml"

done 10<"${list}"
