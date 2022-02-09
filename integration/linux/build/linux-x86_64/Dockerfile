#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM centos:7

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"

ENV LANG C

ENV GPG_KEY E3FF2839C048B25C084DEBE9B26995E310250568
ENV PYTHON_VERSION 3.9.10
ENV GIT_VERSION 2.33.1
ENV PATCHELF_VERSION 0.13
ENV RUSTUP_HOME /usr/local/rustup
ENV CARGO_HOME /usr/local/cargo
ENV PATH /usr/local/cargo/bin:$PATH
ENV RUST_VERSION 1.58.1
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

# Needed to pick up SCL stuff from profile.d/
SHELL ["/bin/bash", "--login", "-c"]

RUN set -ex \
	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
	&& wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
	&& wget -O git.tar.xz "https://mirrors.edge.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz" \
	&& wget -O git.tar.sign "https://mirrors.edge.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.sign" \
	&& wget -O patchelf.tar.bz2 "https://github.com/NixOS/patchelf/releases/download/${PATCHELF_VERSION}/patchelf-${PATCHELF_VERSION}.tar.bz2" \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& echo "disable-ipv6" >> "${GNUPGHOME}/dirmngr.conf" \
	&& (try=1; while [ $try -le 5 ]; do \
		gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$GPG_KEY" && break || true; \
		try=$(( $try + 1 )); sleep 1; done) \
	&& gpg --batch --verify python.tar.xz.asc python.tar.xz \
	&& { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
	&& rm -rf "$GNUPGHOME" python.tar.xz.asc \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	&& mkdir -p /usr/src/git \
	&& tar -xJC /usr/src/git --strip-components=1 -f git.tar.xz \
	&& rm git.tar.xz \
	&& mkdir -p /usr/src/patchelf \
	&& tar -xjC /usr/src/patchelf --strip-components=1 -f patchelf.tar.bz2 \
	&& rm patchelf.tar.bz2 \
	&& cd /usr/src/python \
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
	&& cd /usr/src/patchelf \
	&& ./configure \
	&& make -j $(nproc) \
	&& make install \
	&& rm -rf /usr/src/patchelf \
	&& cd / \
	&& curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- \
		-y --no-modify-path --profile minimal \
		--default-toolchain $RUST_VERSION \
	&& chmod -R a+w $RUSTUP_HOME $CARGO_HOME

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 22.0.3

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
if [ -n "${PKG_VERSION}" ]; then\n\
    extraopts+=" --pkg-version=${PKG_VERSION}"\n\
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
