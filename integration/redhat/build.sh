#!/bin/bash

set -ex

pip install --extra-index-url=https://pypi.magicstack.net/simple/ metapkg
python -m metapkg build --dest=artifacts edgedbpkg.edgedb:EdgeDB
