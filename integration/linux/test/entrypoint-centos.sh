#!/bin/bash

set -ex

if [ "$1" == "bash" ]; then
    exec /bin/bash
fi

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

re="edgedb-server-([[:digit:]]+(-(alpha|beta|rc)[[:digit:]]+)?(-dev[[:digit:]]+)?).*\.rpm"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"

dist='el$releasever'
if [ -n "${PKG_SUBDIST}" ]; then
    dist+=".${PKG_SUBDIST}"
fi

cat <<EOF >/etc/yum.repos.d/edgedb.repo
[edgedb]
name=edgedb
baseurl=https://packages.edgedb.com/rpm/${dist}/
enabled=1
gpgcheck=1
gpgkey=https://packages.edgedb.com/keys/edgedb.asc
EOF

try=1
while [ $try -le 30 ]; do
    yum makecache && yum install --verbose -y edgedb-cli && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

yum install -y "${dest}"/edgedb-server-${slot}*.x86_64.rpm
su edgedb -c "/usr/lib64/edgedb-server-${slot}/bin/python3 \
              -m edb.tools --no-devmode test \
              /usr/share/edgedb-server-${slot}/tests \
              -e cqa_ -e tools_ --output-format=simple"
echo "Success!"
