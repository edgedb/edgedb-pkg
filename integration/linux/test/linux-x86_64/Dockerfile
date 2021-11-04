#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM buildpack-deps:bullseye AS busybox
RUN apt-get update -y \
    && apt-get install -y musl-tools

ENV BUSYBOX_VERSION 1.34.1

RUN set -ex \
	\
    && ln -s /usr/include/x86_64-linux-gnu/asm/ /usr/include/x86_64-linux-musl/asm \
    && ln -s /usr/include/asm-generic/ /usr/include/x86_64-linux-musl/asm-generic \
    && ln -s /usr/include/linux/ /usr/include/x86_64-linux-musl/linux \
    && ln -s /usr/include/mtd/ /usr/include/x86_64-linux-musl/mtd \
	&& curl --proto '=https' --tlsv1.2 -sSf "https://busybox.net/downloads/busybox-${BUSYBOX_VERSION}.tar.bz2" > busybox.tar.bz2 \
	&& mkdir -p /usr/src/busybox \
	&& tar -xjC /usr/src/busybox --strip-components=1 -f busybox.tar.bz2 \
	&& rm busybox.tar.bz2 \
	&& cd /usr/src/busybox \
    && make defconfig \
    && sed -i \
        -e 's/.*CONFIG_STATIC\b.*/CONFIG_STATIC=y/' \
        -e 's/.*CONFIG_FEATURE_PREFER_APPLETS\b.*/CONFIG_FEATURE_PREFER_APPLETS=y/' \
        -e 's/.*CONFIG_FEATURE_SH_STANDALONE\b.*/CONFIG_FEATURE_SH_STANDALONE=y/' \
        .config \
    && cat .config \
    && echo 1 \
	&& make CC=musl-gcc -j "$(nproc)" \
    && cp busybox_unstripped /bin/busybox \
    && chmod +x /bin/busybox

FROM centos:7 AS glibc
RUN curl --proto '=https' --tlsv1.2 -sSfL \
        "https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64" \
        > /bin/jq \
    && chmod +x /bin/jq \
    && curl --proto '=https' --tlsv1.2 -sSfL \
        "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64" \
        > /bin/gosu \
    && chmod +x /bin/gosu

RUN repoquery -l "glibc" "glibc-common" \
	| grep -v --fixed-strings -- '/.build-id' \
	| grep -v --fixed-strings -- '/usr/share/doc' \
	| grep -v --fixed-strings -- '/usr/share/man' \
	| sed 's#^/##g' > "/tmp/contents" \
    && tar \
        --directory=/ \
        --create \
        --no-recursion \
        --sparse \
        --no-seek \
        --files-from=/tmp/contents \
        --file=/tmp/glibc.tar >/dev/null 2>&1 \
        || true

FROM scratch
COPY --from=busybox /bin/busybox /bin/busybox
COPY --from=glibc /bin/jq /bin/jq
COPY --from=glibc /bin/gosu /bin/gosu
COPY --from=glibc /tmp/glibc.tar /tmp/glibc.tar

RUN ["/bin/busybox", "ln", "/bin/busybox", "/bin/sh"]

RUN tar xf /tmp/glibc.tar -C / && rm /tmp/glibc.tar
RUN ln /bin/busybox /bin/echo
RUN /bin/echo -e '#!/bin/sh\n\
\n\
set -ex\n\
\n\
dest="artifacts"\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest="${dest}/${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest="${dest}-${PKG_PLATFORM_VERSION}"\n\
fi\n\
if [ -n "${PKG_TEST_JOBS}" ]; then\n\
    dash_j="-j${PKG_TEST_JOBS}"\n\
else\n\
    dash_j=""\n\
fi\n\
\n\
wget "https://packages.edgedb.com/dist/linux-x86_64/edgedb-cli_latest" \\\n\
    -O /bin/edgedb\n\
chmod +x /bin/edgedb\n\
\n\
tarball=\n\
for pack in ${dest}/*.tar; do\n\
    if [ -e "${pack}" ]; then\n\
        tarball=$(tar -xOf "${pack}" "build-metadata.json" \\\n\
                  | jq -r ".installrefs[]" \\\n\
                  | grep ".tar.gz$")\n\
        if [ -n "${tarball}" ]; then\n\
            break\n\
        fi\n\
    fi\n\
done\n\
\n\
if [ -z "${tarball}" ]; then\n\
    echo "${dest} does not contain a valid build tarball" >&2\n\
    exit 1\n\
fi\n\
\n\
mkdir /edgedb\n\
chmod 1777 /tmp\n\
tar -xOf "${pack}" "${tarball}" | tar -xzf- --strip-components=1 -C "/edgedb/"\n\
touch /etc/group\n\
addgroup edgedb\n\
touch /etc/passwd\n\
adduser -G edgedb -H -D edgedb\n\
\n\
if [ "$1" == "bash" ]; then\n\
    exec /bin/sh\n\
fi\n\
\n\
exec gosu edgedb:edgedb /edgedb/bin/python3 \\\n\
    -m edb.tools --no-devmode test \\\n\
    /edgedb/data/tests \\\n\
    -e cqa_ -e tools_ \\\n\
    --verbose ${dash_j}\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
