#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM centos:7

ENV container docker

STOPSIGNAL SIGRTMIN+3

COPY systemd-spec.patch /tmp/
COPY systemd-patches/* /tmp/systemd-patches/

RUN set -ex \
	&& yum install -y wget rpm-build redhat-rpm-config yum-utils git \
	&& mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS} \
	&& echo '%_topdir /tmp/rpmbuild' > ~/.rpmmacros \
	&& wget -O systemd.src.rpm "http://vault.centos.org/7.6.1810/os/Source/SPackages/systemd-219-62.el7.src.rpm" \
	&& yum-builddep -y systemd.src.rpm \
	&& rpm -i systemd.src.rpm \
	&& rm -f systemd.src.rpm \
	&& cd /tmp/rpmbuild/SPECS \
	&& git apply /tmp/systemd-spec.patch \
	&& cp /tmp/systemd-patches/*.patch /tmp/rpmbuild/SOURCES \
	&& rm -rf /tmp/systemd-spec.patch \
	&& rm -rf /tmp/systemd-patches \
	&& rpmbuild -ba /tmp/rpmbuild/SPECS/systemd.spec \
	&& yum history undo -y last || true \
	&& yum history undo -y last-2 || true \
	&& rpm -e --nodeps systemd systemd-libs \
	&& yum install --exclude systemd-libs.i686 -y \
		/tmp/rpmbuild/RPMS/x86_64/systemd-219-*.el7.x86_64.rpm \
		/tmp/rpmbuild/RPMS/x86_64/systemd-libs-219-*.el7.x86_64.rpm \
	&& rm -rf /tmp/rpmbuild \
	&& rm ~/.rpmmacros \
	&& yum clean all

RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -Exeuo pipefail\n\
\n\
env -0 | while IFS="=" read -r -d "" n v; do printf "%s=\"%s\"\\n" "$n" "$v"; done >/usr/local/env.txt\n\
\n\
cat >/usr/local/bin/script.sh <<EOF\n\
set -euo pipefail\n\
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

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
