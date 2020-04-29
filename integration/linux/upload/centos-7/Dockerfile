#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM centos:7

RUN yum install -y openssh-clients

RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -e\n\
\n\
HOME=$(getent passwd "$(whoami)" | cut -d: -f6)\n\
\n\
mkdir -p "${HOME}/.ssh" && chmod 700 "${HOME}/.ssh"\n\
echo "${PACKAGE_UPLOAD_SSH_KEY}" > "${HOME}/.ssh/id_ed25519"\n\
chmod 400 "${HOME}/.ssh/id_ed25519"\n\
\n\
set -ex\n\
\n\
cat <<EOF >"${HOME}/.ssh/config"\n\
Host upload-packages.edgedb.com\n\
    User uploader\n\
    Port 2223\n\
    StrictHostKeyChecking no\n\
EOF\n\
\n\
dest="artifacts"\n\
key=""\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest+="/${PKG_PLATFORM}"\n\
    key+="-${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
    key+="-${PKG_PLATFORM_VERSION}"\n\
fi\n\
\n\
cd "${dest}"\n\
ls *.rpm > "upload${key}.list"\n\
\n\
cat <<EOF >/tmp/sftp-batch\n\
put *.rpm ./incoming/\n\
put upload${key}.list ./incoming/triggers/\n\
EOF\n\
\n\
sftp -b /tmp/sftp-batch uploader@upload-packages.edgedb.com\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
