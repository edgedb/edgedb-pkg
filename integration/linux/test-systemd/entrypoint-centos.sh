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

re="edgedb-server-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\.rpm"
slot="$(ls ${dest} | sed -n -E "s/${re}/\1/p")"

yum install -y "${dest}"/edgedb-server-common*.x86_64.rpm \
               "${dest}"/edgedb-server-${slot}*.x86_64.rpm

systemctl enable --now edgedb-server-${slot} \
    || (journalctl -u edgedb-server-${slot} && exit 1)

python="/usr/lib64/edgedb-server-${slot}/bin/python3"
edbcli="${python} -m edb.cli"

su edgedb -c "${edbcli} --admin configure insert Auth \
                --method=Trust --priority=0"
[[ "$(echo 'SELECT 1 + 3;' | ${edbcli} -u edgedb)" == *4* ]] || exit 1
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
