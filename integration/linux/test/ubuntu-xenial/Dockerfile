#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:xenial
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
re="edgedb-server-([[:digit:]]+(-(alpha|beta|rc)[[:digit:]]+)?(-dev[[:digit:]]+)?).*\\.deb"\n\
slot="$(ls ${dest} | sed -n -E "s/${re}/\\1/p")"\n\
echo "SLOT=$slot"\n\
\n\
dist="${PKG_PLATFORM_VERSION}"\n\
if [ -n "${PKG_SUBDIST}" ]; then\n\
    dist+=".${PKG_SUBDIST}"\n\
fi\n\
\n\
apt-get update\n\
apt-get install -y curl gnupg apt-transport-https\n\
curl https://packages.edgedb.com/keys/edgedb.asc | apt-key add -\n\
echo deb [arch=amd64] https://packages.edgedb.com/apt ${dist} main \\\n\
    >> /etc/apt/sources.list.d/edgedb.list\n\
\n\
try=1\n\
while [ $try -le 30 ]; do\n\
    apt-get update && apt-get install -y edgedb-cli && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 10 seconds (try #${try})"\n\
    sleep 10\n\
done\n\
\n\
apt-get install -y ./"${dest}"/edgedb-server-${slot}_*_amd64.deb\n\
\n\
if [ "$1" == "bash" ]; then\n\
    echo su edgedb -c \\\n\
        "/usr/lib/x86_64-linux-gnu/edgedb-server-${slot}/bin/python3 \\\n\
         -m edb.tools --no-devmode test \\\n\
         /usr/share/edgedb-server-${slot}/tests \\\n\
         -e cqa_ -e tools_ \\\n\
         --verbose"\n\
    exec "$@"\n\
else\n\
    if [ -n "${PKG_TEST_JOBS}" ]; then\n\
        dash_j="-j${PKG_TEST_JOBS}"\n\
    else\n\
        dash_j=""\n\
    fi\n\
    su edgedb -c \\\n\
        "/usr/lib/x86_64-linux-gnu/edgedb-server-${slot}/bin/python3 \\\n\
         -m edb.tools --no-devmode test \\\n\
         /usr/share/edgedb-server-${slot}/tests \\\n\
         -e cqa_ -e tools_ \\\n\
         --verbose ${dash_j}"\n\
    echo "Success!"\n\
fi\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
