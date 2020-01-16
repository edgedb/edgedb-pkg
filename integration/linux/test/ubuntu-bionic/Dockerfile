#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:bionic
RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -ex\n\
\n\
if [ "$1" == "bash" ]; then\n\
    exec /bin/bash\n\
fi\n\
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
apt-get update\n\
apt install -y ./"${dest}"/edgedb-common_*_amd64.deb \\\n\
               ./"${dest}"/edgedb-${slot}_*_amd64.deb\n\
su edgedb -c "/usr/lib/x86_64-linux-gnu/edgedb-${slot}/bin/python3 \\\n\
              -m edb.tools --no-devmode test /usr/share/edgedb-${slot}/tests \\\n\
              -e cqa_ -e tools_ --output-format=simple"\n\
echo "Success!"\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
