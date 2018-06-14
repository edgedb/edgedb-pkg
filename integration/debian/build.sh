#!/bin/bash

set -ex

export DEBIAN_FRONTEND=noninteractive

apt-get update
pip install --extra-index-url=https://pypi.magicstack.net/simple/ metapkg
python -m metapkg build --dest=artifacts edgedbpkg.edgedb:EdgeDB
