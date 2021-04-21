#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM ubuntu:bionic

COPY dput.patch /tmp/dput.patch

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        patch python3-paramiko dput openssh-client \
    && patch -d /usr/share/dput -p1 </tmp/dput.patch \
    && rm /tmp/dput.patch \
    && apt-get remove -y patch \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -e\n\
\n\
HOME=$(getent passwd "$(whoami)" | cut -d: -f6)\n\
: ${PACKAGE_SERVER:=upload-packages.edgedb.com}\n\
\n\
mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"\n\
if [ -f "${PACKAGE_UPLOAD_SSH_KEY_FILE}" ]; then\n\
    cp "${PACKAGE_UPLOAD_SSH_KEY_FILE}" "${HOME}/.ssh/id_ed25519"\n\
else\n\
    echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"\n\
fi\n\
chmod 400 "${HOME}/.ssh/id_ed25519"\n\
\n\
set -ex\n\
\n\
cat <<EOF >>"${HOME}/.ssh/config"\n\
Host ${PACKAGE_SERVER}\n\
    User uploader\n\
    Port 2223\n\
    StrictHostKeyChecking no\n\
EOF\n\
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
cat <<EOF >/tmp/dput.cf\n\
[edgedb-prod]\n\
fqdn                    = ${PACKAGE_SERVER}\n\
incoming                = /incoming\n\
login                   = uploader\n\
allow_dcut              = 1\n\
method                  = sftp\n\
allow_unsigned_uploads  = 1\n\
EOF\n\
\n\
dput -d -d -c /tmp/dput.cf edgedb-prod "${dest}"/*.changes\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
