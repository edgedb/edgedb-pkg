#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

ARG DOCKER_ARCH=
FROM ${DOCKER_ARCH}buildpack-deps:bullseye AS busybox
RUN apt-get update -y \
    && apt-get install -y musl-tools flex bison

ENV BUSYBOX_VERSION 1.34.1
ENV JQ_VERSION cff5336ec71b6fee396a95bb0e4bea365e0cd1e8

RUN set -ex \
	\
    && machine=$(uname -m) \
    && ln -s /usr/include/${machine}-linux-gnu/asm/ /usr/include/${machine}-linux-musl/asm \
    && ln -s /usr/include/asm-generic/ /usr/include/${machine}-linux-musl/asm-generic \
    && ln -s /usr/include/linux/ /usr/include/${machine}-linux-musl/linux \
    && ln -s /usr/include/mtd/ /usr/include/${machine}-linux-musl/mtd \
    && cd /tmp \
	&& curl --proto '=https' --tlsv1.2 -sSfL "https://busybox.net/downloads/busybox-${BUSYBOX_VERSION}.tar.bz2" -o busybox.tar.bz2 \
	&& mkdir -p /usr/src/busybox \
	&& tar -xjC /usr/src/busybox --strip-components=1 -f busybox.tar.bz2 \
	&& rm busybox.tar.bz2 \
	&& cd /usr/src/busybox \
    && make -j "$(nproc)" defconfig \
    && sed -i \
        -e 's/.*CONFIG_STATIC\b.*/CONFIG_STATIC=y/' \
        -e 's/.*CONFIG_FEATURE_PREFER_APPLETS\b.*/CONFIG_FEATURE_PREFER_APPLETS=y/' \
        -e 's/.*CONFIG_FEATURE_SH_STANDALONE\b.*/CONFIG_FEATURE_SH_STANDALONE=y/' \
        .config \
    && cat .config \
	&& make CC=musl-gcc -j "$(nproc)" \
    && mkdir /build \
    && cp busybox_unstripped /build/busybox \
    && chmod +x /build/busybox \
    && file /build/busybox

RUN set -ex \
    \
    && cd /tmp \
	&& mkdir -p /usr/src/jq \
    && git clone --recursive https://github.com/stedolan/jq /usr/src/jq \
    && cd /usr/src/jq \
    && git reset --hard "${JQ_VERSION}" \
    && autoreconf -fi \
    && ./configure --with-oniguruma=builtin \
    && make LDFLAGS=-all-static -j "$(nproc)" \
    && cp jq /build/jq \
    && chmod +x /build/jq

FROM ${DOCKER_ARCH}golang:1.17-alpine3.15 AS golang
ENV GOSU_VERSION 1.14
ENV CGO_ENABLED 0
RUN set -ex \
	\
    && apk add --no-cache curl \
    && cd /tmp \
	&& curl --proto '=https' --tlsv1.2 -sSfL "https://github.com/tianon/gosu/archive/refs/tags/${GOSU_VERSION}.tar.gz" -o gosu.tar.gz \
	&& mkdir -p /go/src/github.com/tianon/gosu \
	&& tar -xzC /go/src/github.com/tianon/gosu --strip-components=1 -f gosu.tar.gz \
	&& rm gosu.tar.gz \
	&& cd /go/src/github.com/tianon/gosu \
    && go mod download \
    && go mod verify \
    && go build -v -ldflags '-d -s -w' -o /bin/gosu \
    && chmod +x /bin/gosu

FROM ${DOCKER_ARCH}centos:7 AS glibc
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
COPY --from=busybox /build/busybox /bin/busybox
COPY --from=busybox /build/jq /bin/jq
COPY --from=golang /bin/gosu /bin/gosu
COPY --from=glibc /tmp/glibc.tar /tmp/glibc.tar

RUN ["/bin/busybox", "--install", "-s", "/bin/"]
RUN ["/bin/tar", "xvf", "/tmp/glibc.tar", "-C", "/"]
RUN ["/bin/rm", "/tmp/glibc.tar"]
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
machine=$(uname -m)\n\
\n\
wget "https://packages.edgedb.com/dist/${machine}-unknown-linux-musl.nightly/edgedb-cli" \\\n\
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
