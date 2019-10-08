#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:xenial
RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -ex\n\
\n\
export DEBIAN_FRONTEND=noninteractive\n\
\n\
slot="${PKG_VERSION_SLOT}"\n\
\n\
if [ -z "${slot}" ]; then\n\
    echo ::error "Cannot determine package version slot."\n\
    exit 1\n\
fi\n\
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
apt-get update\n\
apt-get install -y edgedb-${slot}\n\
edgedb --help\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
