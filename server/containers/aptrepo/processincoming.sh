#!/bin/bash

set -Eexuo pipefail
shopt -s nullglob

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <changes-file>" >&2
    exit 1
fi

changes=$1
localdir="%%REPREPRO_BASE_DIR%%"
basedir="gs://packages.edgedb-infra.magic.io/apt"

local_dist="${localdir}/"
shared_dist="${basedir}/"

gsutil -m rsync -r -d "${shared_dist}/" "${local_dist}/"
reprepro -v -v --waitforlock 100 processincoming main "${changes}"
mkdir -p "${local_dist}/jsonindexes/"
makeindex.py "${local_dist}" "${local_dist}/jsonindexes"
gsutil -m rsync -r -d "${local_dist}/" "${shared_dist}/"
