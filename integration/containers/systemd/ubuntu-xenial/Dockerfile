#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:xenial

ENV container docker

STOPSIGNAL SIGRTMIN+3

RUN apt-get update && apt-get install -y --no-install-recommends systemd \
	&& rm -rf /var/lib/apt/lists/*

RUN echo '#!/bin/bash\n\
\n\
env -0 | while IFS="=" read -r -d "" n v; do printf "%s=\"%s\"\\n" "$n" "$v"; done >/usr/local/env.txt\n\
\n\
cat >/usr/local/bin/script.sh <<EOF\n\
set -e\n\
\n\
function finish() {\n\
    /bin/systemctl exit \$?\n\
}\n\
\n\
trap finish 0\n\
\n\
${@}\n\
\n\
echo "Script done: $?"\n\
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
exec /lib/systemd/systemd --unit=script.service\n\' >/usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
