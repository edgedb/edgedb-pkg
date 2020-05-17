#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <upload-list>" >&2
    exit 1
fi

list=$1
basedir="gs://packages.edgedb-infra.magic.io"
re="^([[:alnum:]]+(-[[:alpha:]][[:alnum:]]*)?)(-[[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?)?_([^_]*)_([^.]*)(.*)?$"
cd /var/spool/repo/incoming
dists=()

function _cache() {
    gsutil -m setmeta \
        -h "Cache-Control:public, no-transform, max-age=315360000" \
        "${1}"
}

function _no_cache() {
    gsutil -m setmeta \
        -h "Cache-Control:no-store, no-cache, private, max-age=0" \
        "${1}"
}


while read -r -u 10 filename; do
    dist=${filename%%/*}
    distbase=${dist%-*}
    dists+=("${distbase}")
    leafname=$(basename ${filename})
    pkgname="$(echo ${leafname} | sed -n -E "s/${re}/\1/p")"
    if [ -z "${pkgname}" ]; then
        echo "Cannot parse artifact filename: ${filename}" >&2
        exit 1
    fi
    slot="$(echo ${leafname} | sed -n -E "s/${re}/\3/p")"
    release="$(echo ${leafname} | sed -n -E "s/${re}/\7/p")"
    ext="$(echo ${leafname} | sed -n -E "s/${re}/\8/p")"
    subdist=$(echo ${release} | sed 's/[[:digit:]]\+//')
    subdist="${subdist/~/_}"
    pkgdir="${dist}"
    tempdir=$(mktemp -d)
    stgdir="${tempdir}/${pkgdir}"
    distname="${pkgname}${slot}_latest${subdist}${ext}"

    mkdir -p "${stgdir}/"
    cp -a "${filename}" "${stgdir}/"

    gpg --detach-sign --armor "${stgdir}/${leafname}"
    cat "${stgdir}/${leafname}" \
        | sha256sum | cut -f1 -d ' ' > "${stgdir}/${leafname}.sha256"

    archivedir="${basedir}/archive/${pkgdir}"
    gsutil -m cp "${stgdir}/${leafname}" "${archivedir}/${leafname}"
    _cache "${archivedir}/${leafname}"
    gsutil -m cp "${stgdir}/${leafname}.asc" "${archivedir}/${leafname}.asc"
    _cache "${archivedir}/${leafname}.asc"
    gsutil -m cp "${stgdir}/${leafname}.sha256" "${archivedir}/${leafname}.sha256"
    _cache "${archivedir}/${leafname}.sha256"

    targetdir="${basedir}/dist/${pkgdir}"
    gsutil -m cp "${stgdir}/${leafname}" "${targetdir}/${distname}"
    _no_cache "${targetdir}/${distname}"
    gsutil -m cp "${stgdir}/${leafname}.asc" "${targetdir}/${distname}.asc"
    _no_cache "${targetdir}/${distname}.asc"
    gsutil -m cp "${stgdir}/${leafname}.sha256" "${targetdir}/${distname}.sha256"
    _no_cache "${targetdir}/${distname}.sha256"

    rm -rf "${tempdir}"
done 10<"${list}"


for dist in "${dists[@]}"; do
    gsutil ls "${basedir}/archive/${dist}*" \
        | grep -v "\(.sha256\|.asc\)$" \
        | findold.py --keep=3 --subdist=nightly \
        | gsutil -m rm -I || true

    gsutil ls "${basedir}/archive/${dist}*" \
        | sed -e "s|${basedir}/archive/||" \
        | grep -v "\(.sha256\|.asc\)$" \
        | makeindex.py --prefix=/archive/ > "${stgdir}/index.json"

    gsutil -m cp "${stgdir}/index.json" \
        "${basedir}/archive/.jsonindexes/${dist}.json"

    _no_cache "${basedir}/archive/.jsonindexes/${dist}.json"
done
