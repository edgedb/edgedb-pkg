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
re="edgedb-([[:digit:]]+(-(dev|alpha|beta|rc)[[:digit:]]+)?).*\\.rpm"\n\
slot="$(ls ${dest} | sed -n -E "s/${re}/\\1/p")"\n\
\n\
yum install -y "${dest}"/edgedb-common*.x86_64.rpm \\\n\
               "${dest}"/edgedb-${slot}*.x86_64.rpm\n\
su edgedb -c "/usr/lib64/edgedb-${slot}/bin/python3 \\\n\
              -m edb.tools --no-devmode test /usr/share/edgedb-${slot}/tests \\\n\
              -e cqa_ -e tools_ --output-format=simple"\n\
echo "Success!"\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
