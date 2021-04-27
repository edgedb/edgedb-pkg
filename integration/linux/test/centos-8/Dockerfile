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
dest="artifacts"\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest+="/${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
fi\n\
\n\
re="edgedb-server-([[:digit:]]+(-(alpha|beta|rc)[[:digit:]]+)?(-dev[[:digit:]]+)?).*\\.rpm"\n\
slot="$(ls ${dest} | sed -n -E "s/${re}/\\1/p")"\n\
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
    yum makecache && yum install --verbose -y edgedb-cli && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 10 seconds (try #${try})"\n\
    sleep 10\n\
done\n\
\n\
yum install -y "${dest}"/edgedb-server-${slot}*.x86_64.rpm\n\
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
    su edgedb -c \\\n\
        "/usr/lib64/edgedb-server-${slot}/bin/python3 \\\n\
        -m edb.tools --no-devmode test \\\n\
        /usr/share/edgedb-server-${slot}/tests \\\n\
        -e cqa_ -e tools_ \\\n\
        --verbose"\n\
    echo "Success!"\n\
fi\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
