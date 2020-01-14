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

filename=$(basename "${pkg}")
re="^edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?)_([^_]*)_(.*)(\.pkg|tar\..*)$"
slot="$(echo ${filename} | sed -n -E "s/${re}/\1/p")"
release="$(echo ${filename} | sed -n -E "s/${re}/\5/p")"
ext="$(echo ${filename} | sed -n -E "s/${re}/\6/p")"
subdist=$(echo ${release} | sed 's/[[:digit:]]\+//')

if [ ! -e /var/lib/repos/${dist} ]; then
    mkdir /var/lib/repos/${dist}
fi

mkdir -p /tmp/repo-staging/

filename=$(basename "${pkg}")
mv "${pkg}" /tmp/repo-staging
gpg --detach-sign --armor "/tmp/repo-staging/${filename}"
mv /tmp/repo-staging/"${filename}"* "/var/lib/repos/${dist}/"

cp -a "/var/lib/repos/${dist}/${filename}" \
      "/var/lib/repos/${dist}/edgedb-${slot}_latest${subdist}${ext}"

touch "/var/lib/repos/${dist}/edgedb-${slot}_latest${subdist}${ext}"

cp -a "/var/lib/repos/${dist}/${filename}.asc" \
      "/var/lib/repos/${dist}/edgedb-${slot}_latest${subdist}${ext}.asc"

touch "/var/lib/repos/${dist}/edgedb-${slot}_latest${subdist}${ext}.asc"
