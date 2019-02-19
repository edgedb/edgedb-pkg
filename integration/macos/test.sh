#!/bin/bash

set -ex

sudo installer -dumplog -verbose -pkg artifacts/*.pkg -target /Volumes/macOS
sudo su edgedb -c \
    '/Library/Frameworks/EdgeDB.framework/Versions/0/lib/edgedb-0/bin/python3 \
    -m edb.tools --no-devmode test \
    /Library/Frameworks/EdgeDB.framework/Versions/0/share/edgedb-0/tests \
    -e flake8 --output-format=simple'
sudo launchctl enable system/com.edgedb.edgedb-0
[[ "$(echo 'SELECT 1 + 3;' | edgedb -u edgedb)" == *4* ]]
echo "Success!"
