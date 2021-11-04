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
dest="artifacts"\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest+="/${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
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
try=1\n\
while [ $try -le 30 ]; do\n\
    yum makecache && yum install --verbose -y edgedb-cli jq && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 10 seconds (try #${try})"\n\
    sleep 10\n\
done\n\
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
if [ "$1" == "bash" ]; then\n\
    echo su edgedb -c \\\n\
        "/usr/lib64/edgedb-server-${slot}/bin/python3 \\\n\
        -m edb.tools --no-devmode test \\\n\
        /usr/share/edgedb-server-${slot}/tests \\\n\
        -e cqa_ -e tools_ \\\n\
        --verbose"\n\
    exec /bin/bash\n\
else\n\
    if [ -n "${PKG_TEST_JOBS}" ]; then\n\
        dash_j="-j${PKG_TEST_JOBS}"\n\
    else\n\
        dash_j=""\n\
    fi\n\
    su edgedb -c \\\n\
        "/usr/lib64/edgedb-server-${slot}/bin/python3 \\\n\
        -m edb.tools --no-devmode test \\\n\
        /usr/share/edgedb-server-${slot}/tests \\\n\
        -e cqa_ -e tools_ \\\n\
        --verbose ${dash_j}"\n\
    echo "Success!"\n\
fi\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
