#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM fedora:29

ENV container docker

STOPSIGNAL SIGRTMIN+3

RUN yum install -y systemd

RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -Exeuo pipefail\n\
\n\
env -0 | while IFS="=" read -r -d "" n v; do printf "%s=\\"%s\\"\\n" "$n" "$v"; done >/usr/local/env.txt\n\
\n\
cat >/usr/local/bin/script.sh <<'\''EOF'\''\n\
set -xeuo pipefail\n\
\n\
function finish() {\n\
    /bin/systemctl exit $?\n\
}\n\
\n\
trap finish 0\n\
\n\
try=1\n\
while [ $try -le 30 ]; do\n\
    yum makecache \\\n\
    && yum install --enablerepo=edgedb,edgedb-nightly --verbose -y edgedb-cli \\\n\
    && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 10 seconds (try #${try})"\n\
    sleep 10\n\
done\n\
\n\
dest="artifacts"\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest+="/${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
fi\n\
\n\
\n\
slot=\n\
rpm=\n\
for pack in ${dest}/*.tar; do\n\
    if [ -e "${pack}" ]; then\n\
        slot=$(tar -xOf "${pack}" "build-metadata.json" \\\n\
               | jq -r ".version_slot")\n\
        rpm=$(tar -xOf "${pack}" "build-metadata.json" \\\n\
              | jq -r ".contents | keys[]" \\\n\
              | grep "^edgedb-server.*\\.rpm$")\n\
        if [ -n "${rpm}" ]; then\n\
            break\n\
        fi\n\
    fi\n\
done\n\
\n\
if [ -z "${rpm}" ]; then\n\
    echo "${dest} does not seem to contain an edgedb-server .rpm" >&2\n\
    exit 1\n\
fi\n\
\n\
if [ -z "${slot}" ]; then\n\
    echo "could not determine version slot from build metadata" >&2\n\
    exit 1\n\
fi\n\
\n\
tmpdir=$(mktemp -d)\n\
tar -x -C "${tmpdir}" -f "${pack}" "${rpm}"\n\
yum install -y "${tmpdir}/${rpm}"\n\
rm -rf "${tmpdir}"\n\
\n\
systemctl enable --now edgedb-server-${slot} \\\n\
    || (journalctl -u edgedb-server-${slot} && exit 1)\n\
\n\
[[ "$(edgedb --admin -u edgedb query '\''select 1 + 3'\'')" == *4* ]] || exit 1\n\
echo "Success!"\n\
\n\
EOF\n\
\n\
chmod +x /usr/local/bin/script.sh\n\
\n\
mkdir -p /etc/systemd/system\n\
cat >/etc/systemd/system/script.service <<EOF\n\
[Unit]\n\
Description=Main Script\n\
After=syslog.target\n\
After=network.target\n\
\n\
[Service]\n\
Type=oneshot\n\
EnvironmentFile=/usr/local/env.txt\n\
ExecStart=/bin/bash /usr/local/bin/script.sh\n\
StandardOutput=journal+console\n\
StandardError=inherit\n\
\n\
[Install]\n\
WantedBy=multi-user.target\n\
EOF\n\
\n\
systemctl enable script.service\n\
exec /lib/systemd/systemd --unit=script.service\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
