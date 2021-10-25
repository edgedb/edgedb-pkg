#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM debian:bullseye
RUN apt-get update && apt-get install -y --no-install-recommends \
		wget ca-certificates \
	&& rm -rf /var/lib/apt/lists/*
RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -ex\n\
\n\
export DEBIAN_FRONTEND=noninteractive\n\
\n\
install_ref="${PKG_INSTALL_REF}"\n\
\n\
if [ -z "${install_ref}" ]; then\n\
    echo ::error "Cannot determine package install ref."\n\
    exit 1\n\
fi\n\
\n\
dist="${PKG_PLATFORM}-${PKG_PLATFORM_VERSION}"\n\
if [ -n "${PKG_SUBDIST}" ]; then\n\
    dist+=".${PKG_SUBDIST}"\n\
fi\n\
\n\
if [ "$1" == "bash" ]; then\n\
    exec /bin/bash\n\
fi\n\
\n\
url="https://packages.edgedb.com/archive/${dist}/${install_ref}"\n\
\n\
try=1\n\
while [ $try -le 30 ]; do\n\
    wget --secure-protocol=PFS --https-only "${url}" && break || true\n\
    try=$(( $try + 1 ))\n\
    echo "Retrying in 10 seconds (try #${try})"\n\
    sleep 10\n\
done\n\
\n\
artifact=$(basename "${install_ref}")\n\
if ! [ -e "${artifact}" ]; then\n\
    echo ::error "Downloaded something, but `${artifact}` does not exist."\n\
    exit 1\n\
fi\n\
\n\
tdir="edgedb-server-extracted"\n\
mkdir -p "$tdir"\n\
\n\
case "${artifact}" in\n\
    *.tar.gz)\n\
        tar -f "${artifact}" -C "$tdir" -xz --strip-components=1\n\
        ;;\n\
    *.tar.zst)\n\
        tar -f "${artifact}" -C "$tdir" -x --zstd --strip-components=1\n\
        ;;\n\
    *)\n\
        echo ::error "Unrecognized archive: ${archive}"\n\
        exit 1\n\
        ;;\n\
esac\n\
\n\
"${tdir}/bin/edgedb-server" --version\n\
"${tdir}/bin/edgedb-server" --help\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
