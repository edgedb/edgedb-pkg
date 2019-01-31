#!/bin/bash

set -ex

curl -H "Host: files.elvis.hammer.magicstack.net" \
    http://192.168.122.1/build.sh >build.sh
chmod +x build.sh
exec ./build.sh
