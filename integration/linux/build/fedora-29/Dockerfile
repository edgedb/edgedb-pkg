#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM fedora:29

ENV LANG en_US.UTF-8

RUN dnf install -y \
	gcc make python3 python3-wheel git 'dnf-command(builddep)' rsync

RUN /bin/echo -e '#!/bin/bash\n\
\n\
if [ "$1" == "bash" ]; then\n\
    exec /bin/bash\n\
fi\n\
\n\
set -Exeo pipefail\n\
\n\
pip install -U git+https://github.com/edgedb/metapkg\n\
pip install -U git+https://github.com/edgedb/edgedb-pkg\n\
\n\
extraopts=\n\
if [ -n "${SRC_REVISION}" ]; then\n\
    extraopts+=" --source-revision=${SRC_REVISION}"\n\
fi\n\
\n\
if [ -n "${PKG_REVISION}" ]; then\n\
    if [ "${PKG_REVISION}" = "<current-date>" ]; then\n\
        PKG_REVISION="$(date --utc +%Y%m%d%H)"\n\
    fi\n\
    extraopts+=" --pkg-revision=${PKG_REVISION}"\n\
fi\n\
\n\
if [ -n "${PKG_SUBDIST}" ]; then\n\
    extraopts+=" --pkg-subdist=${PKG_SUBDIST}"\n\
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
python -m metapkg build --dest="${dest}" ${extraopts} edgedbpkg.edgedb:EdgeDB\n\
\n\
ls -al "${dest}"\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
