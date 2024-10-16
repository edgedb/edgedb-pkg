#!/usr/bin/env bash

set -ex

: ${GIT_VERSION:=2.33.1}

GIT_KEYS=(
    E1F036B1FEE7221FC778ECEFB0B5E88696AFE6CB
)

mkdir -p /usr/src/git
cd /usr/src

curl -fsSLo git.tar.xz "https://www.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz"
curl -fsSLo git.tar.sign "https://www.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.sign"

for key in "${GIT_KEYS[@]}"; do
    gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" \
    || gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key"
done

# gpg --batch --verify git.tar.sign git.tar.xz
rm -f git.tar.sign

tar -xJC /usr/src/git --strip-components=1 -f git.tar.xz
rm -f git.tar.xz

cd /usr/src/git
make prefix=/usr/local V=1 -j $(nproc) all
make prefix=/usr/local install
cd /usr/src
rm -rf /usr/src/git
