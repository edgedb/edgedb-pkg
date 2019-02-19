#!/bin/bash

set -ex

pip3 install --extra-index-url=https://pypi.magicstack.net/simple/ metapkg
python3 -m metapkg build --dest=artifacts edgedbpkg.edgedb:EdgeDB
