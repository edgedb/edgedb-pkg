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
basedir="s3://edgedb-packages/rpm"
declare -A dists

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
    seendist=${dists[${dist}]+"${dists[${dist}]}"}

    if [ -z "${seendist}" ]; then
        dists["${dist}"]="true"
        mkdir -p "${local_dist}"
        aws s3 sync --delete "${shared_dist}/" "${local_dist}/"
    fi

    if [ ! -e "${local_dist}/repodata/repomd.xml" ]; then
        createrepo --database "${local_dist}"
    fi

    mkdir -p /tmp/repo-staging/
    cp "${pkg}" /tmp/repo-staging
    rm -f "${pkg}"
    echo | rpm --resign "/tmp/repo-staging/${pkgname}"
    mv "/tmp/repo-staging/${pkgname}" "${local_dist}"

    if [ "${subdist}" = "nightly" ]; then
        old_rpms=$(repomanage --keep=3 --old "${local_dist}")
        if [ -n "${old_rpms}" ]; then
            rm "${old_rpms}"
        fi
        remove_old_dev_pkg.py --keep=3 ${local_dist}
    fi

    createrepo --update "${local_dist}"
    gpg --yes --batch --detach-sign --armor "${local_dist}/repodata/repomd.xml"

done 10<"${list}"


for dist in "${!dists[@]}"; do
    local_dist="${localdir}/${dist}"
    shared_dist="${basedir}/${dist}"

    mkdir -p "${localdir}/.jsonindexes/"
    makeindex.py "${localdir}" "${localdir}/.jsonindexes/" "${dist}"

    aws s3 sync --delete \
                --cache-control "public, no-transform, max-age=315360000" \
                --exclude "*" \
                --include "*.rpm" \
                ${local_dist}/ ${shared_dist}/
    aws s3 sync --delete \
                --cache-control "no-store, no-cache, private, max-age=0" \
                ${local_dist}/repodata/ ${shared_dist}/repodata/
    aws s3 sync --delete \
                --cache-control "no-store, no-cache, private, max-age=0" \
                ${localdir}/.jsonindexes/ ${basedir}/.jsonindexes/
done
