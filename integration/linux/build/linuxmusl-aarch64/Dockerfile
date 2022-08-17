#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

ARG DOCKER_ARCH=
FROM ${DOCKER_ARCH}alpine:3.16.2

ENV LANG C.UTF-8
ENV RUST_VERSION 1.62.0

RUN apk add --no-cache \
		bash \
		bison \
		build-base \
		curl \
		flex \
		git \
		linux-headers \
		nodejs \
		patchelf \
		perl \
		python3 \
		python3-dev \
		py3-pip \
		sudo \
		tar \
		yarn \
		zstd

RUN set -x; \
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- \
	-y --no-modify-path --profile minimal \
	--target $(uname -m)-unknown-linux-musl \
	--default-toolchain $RUST_VERSION

ENV PATH /root/.cargo/bin:$PATH

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -Exeo pipefail\n\
\n\
mkdir -p ~/.cache/cargo/{git,registry}\n\
mkdir -p ~/.cargo\n\
rm -rf ~/.cargo/registry ~/.cargo/git\n\
ln -s ~/.cache/cargo/registry ~/.cargo/registry\n\
ln -s ~/.cache/cargo/git ~/.cargo/git\n\
\n\
python -m pip install -U git+https://github.com/edgedb/edgedb-pkg\n\
\n\
if [ -n "${METAPKG_PATH}" ]; then\n\
    p=$(python -c '\''import metapkg;print(metapkg.__path__[0])'\'')\n\
    rm -rf "${p}"\n\
    ln -s "${METAPKG_PATH}" "${p}"\n\
    ls -al "${p}"\n\
fi\n\
\n\
extraopts=\n\
if [ -n "${SRC_REF}" ]; then\n\
    extraopts+=" --source-ref=${SRC_REF}"\n\
fi\n\
\n\
if [ -n "${BUILD_IS_RELEASE}" ]; then\n\
    extraopts+=" --release"\n\
fi\n\
\n\
if [ -n "${PKG_REVISION}" ]; then\n\
    if [ "${PKG_REVISION}" = "<current-date>" ]; then\n\
        PKG_REVISION="$(date --utc +%Y%m%d%H%M)"\n\
    fi\n\
    extraopts+=" --pkg-revision=${PKG_REVISION}"\n\
fi\n\
\n\
if [ -n "${PKG_SUBDIST}" ]; then\n\
    extraopts+=" --pkg-subdist=${PKG_SUBDIST}"\n\
fi\n\
\n\
if [ -n "${EXTRA_OPTIMIZATIONS}" ]; then\n\
    extraopts+=" --extra-optimizations"\n\
fi\n\
\n\
if [ -n "${BUILD_GENERIC}" ]; then\n\
    extraopts+=" --generic"\n\
fi\n\
\n\
if [ -n "${PKG_BUILD_JOBS}" ]; then\n\
    extraopts+=" --jobs=${PKG_BUILD_JOBS}"\n\
fi\n\
\n\
dest="artifacts"\n\
if [ -n "${PKG_PLATFORM}" ]; then\n\
    dest+="/${PKG_PLATFORM}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_LIBC}" ]; then\n\
    extraopts+=" --libc=${PKG_PLATFORM_LIBC}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_ARCH}" ]; then\n\
    extraopts+=" --arch=${PKG_PLATFORM_ARCH}"\n\
fi\n\
\n\
if [ -z "${PACKAGE}" ]; then\n\
    PACKAGE="edgedbpkg.edgedb:EdgeDB"\n\
fi\n\
\n\
if [ "$1" == "bash" ] || [ "${GET_SHELL}" == "true" ]; then\n\
    echo python -m metapkg build --dest="${dest}" ${extraopts} "${PACKAGE}"\n\
    exec /bin/bash\n\
else\n\
    python -m metapkg build -vvv --dest="${dest}" ${extraopts} "${PACKAGE}"\n\
    ls -al "${dest}"\n\
fi\n\' >/entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
