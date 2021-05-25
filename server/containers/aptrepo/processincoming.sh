#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <changes-file>" >&2
    exit 1
fi

changes=$1
localdir="%%REPREPRO_BASE_DIR%%"
basedir="s3://edgedb-packages/apt"

local_dist="${localdir}/"
shared_dist="${basedir}/"

aws s3 sync --delete --exact-timestamps \
    "${shared_dist}db/" "${local_dist}db/"

aws s3 sync --delete --exact-timestamps \
    "${shared_dist}dists/" "${local_dist}dists/"

aws s3 sync --delete --exact-timestamps \
    "${shared_dist}.jsonindexes/" "${local_dist}.jsonindexes/"

aws s3 sync --delete \
    "${shared_dist}pool/" "${local_dist}pool/"

reprepro -v -v --waitforlock 100 processincoming main "${changes}"
mkdir -p "${local_dist}/.jsonindexes/"
makeindex.py "${local_dist}" "${local_dist}/.jsonindexes"
aws s3 sync --delete \
            --cache-control "no-store, no-cache, private, max-age=0" \
            "${local_dist}db/" "${shared_dist}db/"
aws s3 sync --delete \
            --cache-control "no-store, no-cache, private, max-age=0" \
            "${local_dist}dists/" "${shared_dist}dists/"
aws s3 sync --delete \
            --cache-control "no-store, no-cache, private, max-age=0" \
            "${local_dist}.jsonindexes/" "${shared_dist}.jsonindexes/"
aws s3 sync --delete \
            --cache-control "public, no-transform, max-age=315360000" \
            "${local_dist}pool/" "${shared_dist}pool/"
