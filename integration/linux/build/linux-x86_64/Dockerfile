#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

ARG DOCKER_ARCH=
FROM ${DOCKER_ARCH}centos:7

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:/usr/local/cargo/bin:/usr/local/go/bin:$PATH
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"

ENV LANG C

ENV GPG_KEY %%PLACEHOLDER%%
ENV PYTHON_VERSION 3.9.15
ENV GIT_VERSION 2.33.1
ENV PATCHELF_VERSION 0.13
ENV TAR_VERSION latest
ENV RUSTUP_HOME /usr/local/rustup
ENV CARGO_HOME /usr/local/cargo
ENV GO_VERSION 1.18.4
ENV RUST_VERSION 1.63.0
ENV NODE_VERSION 16.16.0
ENV YARN_VERSION 1.22.19
ENV GCC_VERSION 10


RUN yum install -y centos-release-scl epel-release \
	&& yum install -y \
	devtoolset-${GCC_VERSION} make patch flex bison \
    wget zlib-devel openssl-devel sqlite-devel bzip2 bzip2-devel \
    expat-devel ncurses-devel gdbm-devel readline-devel libuuid-devel \
	curl-devel xz-devel libffi-devel gettext \
    perl-Getopt-Long perl-IPC-Cmd perl-Data-Dumper \
	sudo ca-certificates zstd

RUN printf "#!/bin/bash\nsource scl_source enable devtoolset-${GCC_VERSION}" \
	> /etc/profile.d/enabledevtoolset${GCC_VERSION}.sh

# aarch64 images somehow don't have the en_US locale
RUN localedef -f UTF-8 -i en_US en_US.UTF-8

# Needed to pick up SCL stuff from profile.d/
SHELL ["/bin/bash", "--login", "-c"]

RUN set -ex \
	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
	&& wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
	&& wget -O git.tar.xz "https://mirrors.edge.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz" \
	&& wget -O git.tar.sign "https://mirrors.edge.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.sign" \
	&& wget -O patchelf.tar.bz2 "https://github.com/NixOS/patchelf/releases/download/${PATCHELF_VERSION}/patchelf-${PATCHELF_VERSION}.tar.bz2" \
	&& wget -O tar.tar.xz "https://alpha.gnu.org/gnu/tar/tar-${TAR_VERSION}.tar.xz" \
	&& wget -O tar.tar.xz.sign "https://alpha.gnu.org/gnu/tar/tar-${TAR_VERSION}.tar.xz.sig" \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& echo "disable-ipv6" >> "${GNUPGHOME}/dirmngr.conf" \
    && for key in \
      E3FF2839C048B25C084DEBE9B26995E310250568 \
      a035c8c19219ba821ecea86b64e628f8d684696d \
    ; do \
      gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" || \
      gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" ; \
    done \
    && for key in \
      4ED778F539E3634C779C87C6D7062848A1AB005C \
      141F07595B7B3FFE74309A937405533BE57C7D57 \
      94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
      74F12602B6F1C4E913FAA37AD3A89613643B6201 \
      71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
      8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 \
      C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
      C82FA3AE1CBEDC6BE46B9360C43CEC45C17AB93C \
      DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
      A48C2BEE680E841632CD4E44F07496B3EB3C1762 \
      108F52B48DB57BB0CC439B2997B01419BD92F80A \
      B9E2F5981AA6E0CD28160D9FF13993A75599653C \
    ; do \
      gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" || \
      gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" ; \
    done \
    && for key in \
      6A010C5166006599AA17F08146C2130DFD2497F5 \
    ; do \
      gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" || \
      gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" ; \
    done \
    && for key in \
      7E3792A9D8ACF7D633BC1588ED97E90E62AA7E34 \
      325F650C4C2B6AD58807327A3602B07F55D0C732 \
    ; do \
      gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" || \
      gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" ; \
    done \
	&& gpg --batch --verify python.tar.xz.asc python.tar.xz \
	&& rm -rf python.tar.xz.asc \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	&& mkdir -p /usr/src/git \
	&& tar -xJC /usr/src/git --strip-components=1 -f git.tar.xz \
	&& rm git.tar.xz \
	&& gpg --batch --verify tar.tar.xz.sign tar.tar.xz \
	&& rm -rf tar.tar.xz.sign \
	&& mkdir -p /usr/src/tar \
	&& tar -xJC /usr/src/tar --strip-components=1 -f tar.tar.xz \
	&& rm tar.tar.xz \
	&& mkdir -p /usr/src/patchelf \
	&& tar -xjC /usr/src/patchelf --strip-components=1 -f patchelf.tar.bz2 \
	&& rm patchelf.tar.bz2 \
	&& cd /usr/src/python \
	\
	&& gnuArch="$(gcc -dumpmachine)" \
	&& ./configure \
		--build="$gnuArch" \
		--enable-loadable-sqlite-extensions \
		--enable-shared \
		--with-system-expat \
		--with-system-ffi \
		--without-ensurepip \
	&& make -j "$(nproc)" \
	&& make install \
	&& ldconfig \
	\
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm -rf /usr/src/python \
	\
	&& cd /usr/src/git \
	&& make prefix=/usr/local V=1 -j $(nproc) all \
	&& make prefix=/usr/local install \
	&& rm -rf /usr/src/git \
	&& cd /usr/src/tar \
	&& env FORCE_UNSAFE_CONFIGURE=1 ./configure \
		--bindir=/usr/local/bin/ \
		--libexecdir=/usr/local/sbin/ \
	&& make -j $(nproc) \
	&& make install \
	&& rm -rf /usr/src/tar \
	&& cd /usr/src/patchelf \
	&& ./configure \
	&& make -j $(nproc) \
	&& make install \
	&& rm -rf /usr/src/patchelf \
	&& cd / \
	&& curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- \
		-y --no-modify-path --profile minimal \
		--default-toolchain $RUST_VERSION \
	&& chmod -R a+w $RUSTUP_HOME $CARGO_HOME \
	\
	&& dpkgArch="$(rpm --eval '%{_arch}')" \
	&& case "${dpkgArch##*-}" in \
		x86_64) \
			NODE_ARCH='x64' \
			GO_ARCH='amd64' \
			;; \
		ppc64el) \
			NODE_ARCH='ppc64le' \
			GO_ARCH='ppc64le' \
			;; \
		s390x) \
			NODE_ARCH='s390x' \
			GO_ARCH='s390x' \
			;; \
		arm64) \
			NODE_ARCH='arm64' \
			GO_ARCH='arm64' \
			;; \
		aarch64) \
			NODE_ARCH='arm64' \
			GO_ARCH='arm64' \
			;; \
		i386) \
			NODE_ARCH='x86' \
			GO_ARCH='386' \
			;; \
		*) echo "unsupported architecture"; exit 1 ;; \
	esac \
	&& curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-${NODE_ARCH}.tar.xz" \
	&& curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
	&& gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc \
	&& grep " node-v$NODE_VERSION-linux-${NODE_ARCH}.tar.xz\$" SHASUMS256.txt | sha256sum -c - \
	&& tar -xJf "node-v$NODE_VERSION-linux-${NODE_ARCH}.tar.xz" -C /usr/local --strip-components=1 --no-same-owner \
	&& rm "node-v$NODE_VERSION-linux-${NODE_ARCH}.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt \
	&& ln -s /usr/local/bin/node /usr/local/bin/nodejs \
	&& curl -fsSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz" \
	&& curl -fsSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz.asc" \
	&& gpg --batch --verify yarn-v$YARN_VERSION.tar.gz.asc yarn-v$YARN_VERSION.tar.gz \
	&& mkdir -p /opt \
	&& tar -xzf yarn-v$YARN_VERSION.tar.gz -C /opt/ \
	&& ln -s /opt/yarn-v$YARN_VERSION/bin/yarn /usr/local/bin/yarn \
	&& ln -s /opt/yarn-v$YARN_VERSION/bin/yarnpkg /usr/local/bin/yarnpkg \
	&& rm yarn-v$YARN_VERSION.tar.gz.asc yarn-v$YARN_VERSION.tar.gz \
	&& curl --proto '=https' --tlsv1.2 -sSfL \
		https://go.dev/dl/go${GO_VERSION}.linux-${GO_ARCH}.tar.gz -o /tmp/go.tgz \
	&& tar -C /usr/local -xzf /tmp/go.tgz \
	&& rm /tmp/go.tgz \
	&& { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
	&& rm -rf "$GNUPGHOME" \
	\
	&& python3 --version \
	&& rustc --version \
	&& node --version \
	&& npm --version \
	&& yarn --version \
	&& git --version \
	&& tar --version

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 22.3

RUN set -ex; \
	\
	wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py'; \
	\
	python get-pip.py \
		--disable-pip-version-check \
		"pip==$PYTHON_PIP_VERSION" \
	; \
	pip --version; \
	\
	find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' +; \
	rm -f get-pip.py

RUN /bin/echo -e '#!/bin/bash\n\
\n\
set -Exeo pipefail\n\
\n\
: "${CARGO_HOME:=$HOME/.cargo}"\n\
\n\
mkdir -p ~/.cache/cargo/{git,registry}\n\
mkdir -p "$CARGO_HOME"\n\
rm -rf "${CARGO_HOME}"/{git,registry}\n\
ln -s ~/.cache/cargo/registry "${CARGO_HOME}/registry"\n\
ln -s ~/.cache/cargo/git "${CARGO_HOME}/git"\n\
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
if [ -n "${PKG_PLATFORM_LIBC}" ]; then\n\
    dest+="${PKG_PLATFORM_LIBC}"\n\
    extraopts+=" --libc=${PKG_PLATFORM_LIBC}"\n\
fi\n\
if [ -n "${PKG_PLATFORM_VERSION}" ]; then\n\
    dest+="-${PKG_PLATFORM_VERSION}"\n\
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

RUN gcc --version \
	&& python3 --version \
	&& git --version \
	&& rustc --version \
	&& patchelf --version

ENTRYPOINT ["/bin/sh", "--login", "-c", "/entrypoint.sh"]
