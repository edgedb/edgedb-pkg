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
basedir="gs://packages.edgedb-infra.magic.io/rpm"

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

    gsutil -m rsync -r -d "${shared_dist}/" "${local_dist}/"

    if [ ! -e "${local_dist}/repodata/repomd.xml" ]; then
        createrepo --database "${local_dist}"
    fi

    mkdir -p /tmp/repo-staging/
    mv "${pkg}" /tmp/repo-staging
    echo | rpm --resign "/tmp/repo-staging/${pkgname}"
    mv "/tmp/repo-staging/${pkgname}" "${local_dist}"

    if [ "${subdist}" = "nightly" ]; then
        old_rpms=$(repomanage --keep=3 --old "${local_dist}")
        if [ -n "${old_rpms}" ]; then
            rm "${old_rpms}"
        fi
    fi

    createrepo --update "${local_dist}"
    gpg --yes --batch --detach-sign --armor "${local_dist}/repodata/repomd.xml"
    mkdir -p "${localdir}/jsonindexes/"
    makeindex.py "${localdir}" "${localdir}/jsonindexes/" "${dist}"

    gsutil -m rsync -r -d "${local_dist}/" "${shared_dist}/"
    gsutil -m rsync -r -d \
        "${localdir}/jsonindexes/" "${shared_dist}/jsonindexes/"

done 10<"${list}"
