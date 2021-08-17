#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM centos:8
RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -ex\n\
\n\
install_ref="${PKG_INSTALL_REF}"\n\
\n\
if [ -z "${install_ref}" ]; then\n\
    echo ::error "Cannot determine package install ref."\n\
    exit 1\n\
fi\n\
\n\
slot="${PKG_VERSION_SLOT}"\n\
\n\
if [ -z "${slot}" ]; then\n\
    echo ::error "Cannot determine package version slot."\n\
    exit 1\n\
fi\n\
\n\
dist='\''el$releasever'\''\n\
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
if [ "$1" == "bash" ]; then\n\
    exec /bin/bash\n\
fi\n\
\n\
try=1\n\
while [ $try -le 30 ]; do\n\
    yum makecache && yum install --verbose -y "${install_ref}" && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 10 seconds (try #${try})"\n\
    sleep 10\n\
done\n\
\n\
edgedb-server-${slot} --help\n\
edgedb --help\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
