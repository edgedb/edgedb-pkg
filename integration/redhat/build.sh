#!/bin/bash

set -ex

pip3 install --extra-index-url=https://pypi.magicstack.net/simple/ metapkg

extraopts=
if [ -n "${EDGEDB_TAG}" ]; then
    extraopts+=" --tag=${EDGEDB_TAG}"
fi

python3 -m metapkg build --dest=artifacts ${extraopts} edgedbpkg.edgedb:EdgeDB
