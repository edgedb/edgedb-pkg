#!/bin/bash

set -Exeuo pipefail

env -0 | while IFS="=" read -r -d "" n v; do printf "%s=\"%s\"\\n" "$n" "$v"; done >/usr/local/env.txt

cat >/usr/local/bin/script.sh <<'EOF'
set -xeuo pipefail

function finish() {
    /bin/systemctl exit $?
}

trap finish 0

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.rpm"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"

yum install -y "${dest}"/edgedb-common*.x86_64.rpm \
               "${dest}"/edgedb-${slot}*.x86_64.rpm

systemctl enable --now edgedb-${slot} \
    || (journalctl -u edgedb-${slot} && exit 1)

su edgedb -c 'edgedb --admin configure insert auth \
                --method=trust --priority=0'
[[ "$(echo 'SELECT 1 + 3;' | edgedb -u edgedb)" == *4* ]] || exit 1
echo "Success!"

EOF

chmod +x /usr/local/bin/script.sh

cat >/etc/systemd/system/script.service <<EOF
[Unit]
Description=Main Script
After=syslog.target
After=network.target

[Service]
Type=oneshot
EnvironmentFile=/usr/local/env.txt
ExecStart=/bin/bash /usr/local/bin/script.sh
StandardOutput=journal+console
StandardError=inherit

[Install]
WantedBy=multi-user.target
EOF

systemctl enable script.service
exec /lib/systemd/systemd --unit=script.service