#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM centos:7
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
repo="edgedb"\n\
if [ -n "${PKG_SUBDIST}" ]; then\n\
    repo+="-${PKG_SUBDIST}"\n\
fi\n\
\n\
curl -fL https://packages.edgedb.com/rpm/edgedb-rhel.repo \\\n\
    >/etc/yum.repos.d/edgedb.repo\n\
\n\
if [ "$1" == "bash" ]; then\n\
    exec /bin/bash\n\
fi\n\
\n\
try=1\n\
while [ $try -le 30 ]; do\n\
    yum makecache --enablerepo="${repo}" \\\n\
    && yum install --enablerepo="${repo}" --verbose -y "${install_ref}" \\\n\
    && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 30 seconds (try #${try})"\n\
    sleep 30\n\
done\n\
\n\
if [ "${PKG_NAME}" == "edgedb-cli" ]; then\n\
    edgedb --help\n\
    edgedb --version\n\
else\n\
    slot="${PKG_VERSION_SLOT}"\n\
\n\
    if [ -z "${slot}" ]; then\n\
        echo ::error "Cannot determine package version slot."\n\
        exit 1\n\
    fi\n\
\n\
    edgedb-server-${slot} --help\n\
    edgedb-server-${slot} --version\n\
fi\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# rpm on centos 7 iterates over all fds up to the limit, which is
# extremely slow. Force it to be small with ulimit.
#
# We need to disable the mirrorlist and explicitly set up a
# baseurl. Switch to the archive.kernel.org mirror while we are at it.
RUN ulimit -n 1024 \
    && sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* \
    && sed -i 's|# \?baseurl=http://mirror.centos.org|baseurl=https://archive.kernel.org/centos-vault/|g' /etc/yum.repos.d/CentOS-* \
    && yum update -y
