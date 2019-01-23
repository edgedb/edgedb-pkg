#!/bin/sh

env >/usr/local/env.txt

cat >/usr/local/bin/script.sh <<EOF
set -e

function finish() {
    /bin/systemctl exit \$?
}

trap finish 0

${@}
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
