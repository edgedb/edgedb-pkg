#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <upload-list>" >&2
    exit 1
fi

list=$1
incomingdir="%%REPO_INCOMING_DIR%%"
localdir="%%REPO_LOCAL_DIR%%"
basedir="%%REPO_BASE_DIR%%"

# createrepo seems to be really broken on gcsfuse
# https://github.com/GoogleCloudPlatform/gcsfuse/issues/321
# so, as a workaround, update the repo using a local copy,
# and rsync the final result to gcs.

while read -r -u 10 pkgname; do

    pkg="${incomingdir}/${pkgname}"
    release=$(rpm -qp --queryformat '%{RELEASE}' "${pkg}")
    dist=${release##*.}
    releaseno=${release%.*}
    subdist=$(echo ${releaseno} | sed 's/[[:digit:]]\+//')
    if [ -n "${subdist}" ]; then
        dist="${dist}.${subdist}"
    fi

    case "${dist}" in
        el7*)
            ;;
        el8*)
            ;;
        *)
            echo "Unsupported dist: ${dist}" >&2; exit 1 ;;
    esac

    local_dist="${localdir}/${dist}"
    shared_dist="${basedir}/${dist}"

    mkdir -p "${local_dist}"

    if [ ! -e "${shared_dist}" ]; then
        createrepo --database "${local_dist}"
    else
        rsync -av "${shared_dist}/" "${local_dist}/"
    fi

    mkdir -p /tmp/repo-staging/
    mv "${pkg}" /tmp/repo-staging
    echo | rpm --resign "/tmp/repo-staging/${pkgname}"
    mv "/tmp/repo-staging/${pkgname}" "${local_dist}"

    if [ "${subdist}" = "nightly" ]; then
        rm $(repomanage --keep=3 --old "${local_dist}")
    fi

    createrepo --update "${local_dist}"
    gpg --yes --batch --detach-sign --armor "${local_dist}/repodata/repomd.xml"

    rsync -av --delete "${local_dist}/" "${shared_dist}/"

done 10<"${list}"
