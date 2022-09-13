#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM debian:buster

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        openssh-client \
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
cat <<EOF >"${HOME}/.ssh/config"\n\
Host ${PACKAGE_SERVER}\n\
    User uploader\n\
    Port 2222\n\
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
if [ -n "${PKG_PLATFORM_LIBC}" ]; then\n\
    dest+="${PKG_PLATFORM_LIBC}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
fi\n\
\n\
cd "${dest}"\n\
list=$(mktemp)\n\
batch=$(mktemp)\n\
find . -type f -printf '\''%P\\n'\'' > "${list}"\n\
chmod g+rw "${list}"\n\
\n\
cat <<EOF >${batch}\n\
put -r * incoming/\n\
put -p ${list} incoming/triggers/\n\
EOF\n\
\n\
sftp -b "${batch}" uploader@"$PACKAGE_SERVER"\n\
\n\
rm "${list}" "${batch}"\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
