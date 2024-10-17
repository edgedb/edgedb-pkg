#!/usr/bin/env bash

set -ex

: ${GZIP_VERSION:=1.13}

GZIP_KEYS=(
    155D3FC500C834486D1EEA677FD9FCCB000BEEEE
)

mkdir -p /usr/src/gzip
cd /usr/src

curl -fsSLo gzip.tar.gz "https://ftp.gnu.org/gnu/gzip/gzip-${GZIP_VERSION}.tar.gz"
curl -fsSLo gzip.tar.gz.sign "https://ftp.gnu.org/gnu/gzip/gzip-${GZIP_VERSION}.tar.gz.sig"

for key in "${GZIP_KEYS[@]}"; do
    gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" \
    || gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key"
done

gpg --batch --verify gzip.tar.gz.sign gzip.tar.gz
rm -f gzip.tar.gz.sign

tar -xzC /usr/src/gzip --strip-components=1 -f gzip.tar.gz
rm -f gzip.tar.gz

cd /usr/src/gzip
./configure \
	--bindir=/usr/local/bin/ \
	--libexecdir=/usr/local/sbin/
make -j $(nproc)
make install
cd /usr/src
rm -rf /usr/src/gzip
