#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:xenial

ENV container docker

STOPSIGNAL SIGRTMIN+3

RUN apt-get update && apt-get install -y --no-install-recommends systemd \
	&& rm -rf /var/lib/apt/lists/*

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
dest="artifacts"\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest+="/${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
fi\n\
\n\
re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\\.deb"\n\
slot="$(ls ${dest} | sed -n -E "s/${re}/\\1/p")"\n\
echo "SLOT=$slot"\n\
\n\
export DEBIAN_FRONTEND=noninteractive\n\
apt-get update\n\
apt install -y ./"${dest}"/edgedb-common_*_amd64.deb \\\n\
               ./"${dest}"/edgedb-${slot}_*_amd64.deb\n\
systemctl enable --now edgedb-${slot} \\\n\
    || (journalctl -u edgedb-${slot} && exit 1)\n\
\n\
su edgedb -c '\''edgedb --admin configure insert auth \\\n\
                --method=trust --priority=0'\''\n\
[[ "$(echo '\''SELECT 1 + 3;'\'' | edgedb -u edgedb)" == *4* ]] || exit 1\n\
echo "Success!"\n\
\n\
EOF\n\
\n\
chmod +x /usr/local/bin/script.sh\n\
\n\
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
