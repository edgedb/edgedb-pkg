#!/bin/bash

set -Exeuo pipefail

env -0 | while IFS="=" read -r -d "" n v; do printf "%s=\"%s\"\\n" "$n" "$v"; done >/usr/local/env.txt

cat >/usr/local/bin/script.sh <<'EOF'
set -xeuo pipefail

function finish() {
    /bin/systemctl exit $?
}

trap finish 0

export DEBIAN_FRONTEND=noninteractive

dest="artifacts"
if [ -n "${PKG_PLATFORM}" ]; then
    dest+="/${PKG_PLATFORM}"
fi
if [ -n "${PKG_PLATFORM_VERSION}" ]; then
    dest+="-${PKG_PLATFORM_VERSION}"
fi

dist="${PKG_PLATFORM_VERSION}"

apt-get update
curl https://packages.edgedb.com/keys/edgedb.asc | apt-key add -
echo deb https://packages.edgedb.com/apt "${dist}" "${PKG_SUBDIST:-main}" \
    >> /etc/apt/sources.list.d/edgedb.list

try=1
while [ $try -le 30 ]; do
    apt-get update && apt-get install -y edgedb-cli && break || true
    try=$(( $try + 1 ))
    echo "Retrying in 10 seconds (try #${try})"
    sleep 10
done

slot=
deb=
for pack in ${dest}/*.tar; do
    if [ -e "${pack}" ]; then
        slot=$(tar -xOf "${pack}" "build-metadata.json" \
               | jq -r ".version_slot")
        deb=$(tar -xOf "${pack}" "build-metadata.json" \
              | jq -r ".contents | keys[]" \
              | grep "^edgedb-server.*\\.deb$")
        if [ -n "${deb}" ]; then
            break
        fi
    fi
done

if [ -z "${deb}" ]; then
    echo "${dest} does not seem to contain an edgedb-server .deb" >&2
    exit 1
fi

if [ -z "${slot}" ]; then
    echo "could not determine version slot from build metadata" >&2
    exit 1
fi

tmpdir=$(mktemp -d)
tar -x -C "${tmpdir}" -f "${pack}" "${deb}"
apt-get install -y "${tmpdir}/${deb}"
rm -rf "${tmpdir}"

systemctl enable --now edgedb-server-${slot} \
    || (journalctl -u edgedb-server-${slot} && exit 1)

ls -al /var/run/edgedb/

python="/usr/lib/x86_64-linux-gnu/edgedb-server-${slot}/bin/python3"
[[ "$(edgedb --admin -P5656 query 'SELECT 1 + 3;')" == *4* ]] || exit 1
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
