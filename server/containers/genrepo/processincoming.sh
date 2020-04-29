#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <upload-list>" >&2
    exit 1
fi

list=$1
re="^([[:alnum:]]+(-[[:alpha:]][[:alnum:]]*)?)(-[[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?)?_([^_]*)_(.*)(\.pkg|\.zip|\.tar\..*)?$"
cd /var/spool/repo/incoming

while read -r -u 10 filename; do
    dist=${filename%%/*}
    pkg=${filename#*/}
    leafname=$(basename ${filename})
    pkgname="$(echo ${pkg} | sed -n -E "s/${re}/\1/p")"
    if [ -z "${pkgname}" ]; then
        echo "Cannot parse artifact filename: ${pkg}" >&2
        exit 1
    fi
    slot="$(echo ${pkg} | sed -n -E "s/${re}/\3/p")"
    release="$(echo ${pkg} | sed -n -E "s/${re}/\7/p")"
    ext="$(echo ${pkg} | sed -n -E "s/${re}/\8/p")"
    subdist=$(echo ${release} | sed 's/[[:digit:]]\+//')
    pkgdir="${dist}"
    pkg=${pkg%%/*}
    tempdir=$(mktemp -d)
    stgdir="${tempdir}/${pkgdir}"
    targetdir="/var/lib/repos/dist/${pkgdir}"
    distname="${pkgname}${slot}_latest${subdist}${ext}"

    mkdir -p "${stgdir}/"
    cp -a "${filename}" "${stgdir}/"

    gpg --detach-sign --armor "${stgdir}/${leafname}"
    cat "${stgdir}/${leafname}" \
        | sha256sum | cut -f1 -d ' ' > "${stgdir}/${leafname}.sha256"

    if [ "${subdist}" != ".nightly" ]; then
        archivedir="/var/lib/repos/archive/${pkgdir}"
        mkdir -p "${archivedir}/"
        cp -a "${stgdir}/${leafname}"* "${archivedir}/"
    fi

    mkdir -p "${targetdir}/"
    mv "${stgdir}/${leafname}" "${targetdir}/${distname}"
    touch "${targetdir}/${distname}"
    mv "${stgdir}/${leafname}.asc" "${targetdir}/${distname}.asc"
    touch "${targetdir}/${distname}.asc"
    mv "${stgdir}/${leafname}.sha256" "${targetdir}/${distname}.sha256"
    touch "${targetdir}/${distname}.sha256"

    rm -rf "${tempdir}"

done 10<"${list}"
