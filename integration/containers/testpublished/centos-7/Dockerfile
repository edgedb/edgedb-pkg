#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM centos:7
RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -ex\n\
\n\
slot="${PKG_VERSION_SLOT}"\n\
\n\
if [ -z "${slot}" ]; then\n\
    echo ::error "Cannot determine package version slot."\n\
    exit 1\n\
fi\n\
\n\
dist='\''el\\$releasever'\''\n\
if [ -n "${PKG_SUBDIST}" ]; then\n\
    dist+=".${PKG_SUBDIST}"\n\
fi\n\
\n\
cat <<EOF >/etc/yum.repos.d/edgedb.repo\n\
[edgedb]\n\
name=edgedb\n\
baseurl=https://packages.edgedb.com/rpm/${dist}/\n\
enabled=1\n\
gpgcheck=1\n\
gpgkey=https://packages.edgedb.com/keys/edgedb.asc\n\
EOF\n\
\n\
echo "Pausing for 2 minutes to let the package repo settle..."\n\
sleep 120\n\
\n\
yum install -y edgedb-${slot}\n\
edgedb --help\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
