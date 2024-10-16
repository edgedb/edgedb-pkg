#!/usr/bin/env bash

set -ex

: ${OPENSSL_VERSION:=3.3.2}

OPENSSL_KEYS=(
    BA5473A2B0587B07FB27CF2D216094DFD0CB81EF
    EFC0A467D613CB83C7ED6D30D894E2CE8B3D79F5
)

mkdir -p /usr/src/openssl
cd /usr/src

if [[ $OPENSSL_VERSION == 1.* ]]; then
    curl -fsSLo openssl.tar.gz "https://github.com/openssl/openssl/releases/download/OpenSSL_${OPENSSL_VERSION//./_}/openssl-${OPENSSL_VERSION}.tar.gz"
    curl -fsSLo openssl.tar.gz.asc "https://github.com/openssl/openssl/releases/download/OpenSSL_${OPENSSL_VERSION//./_}/openssl-${OPENSSL_VERSION}.tar.gz.asc"
else
    curl -fsSLo openssl.tar.gz "https://github.com/openssl/openssl/releases/download/openssl-${OPENSSL_VERSION}/openssl-${OPENSSL_VERSION}.tar.gz"
    curl -fsSLo openssl.tar.gz.asc "https://github.com/openssl/openssl/releases/download/openssl-${OPENSSL_VERSION}/openssl-${OPENSSL_VERSION}.tar.gz.asc"
fi

for key in "${OPENSSL_KEYS[@]}"; do
    gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$key" \
    || gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key"
done

gpg --batch --verify openssl.tar.gz.asc openssl.tar.gz
rm -f openssl.tar.gz.asc

tar -xzC /usr/src/openssl --strip-components=1 -f openssl.tar.gz
rm -f openssl.tar.gz

cd /usr/src/openssl

./config \
    --prefix="/usr/local/openssl" \
    --openssldir="/usr/local/openssl/etc/ssl" \
    --libdir="/usr/local/openssl/lib" \
    "no-ssl3" \
    "shared"

make -j "$(nproc)"
make -j "$(nproc)" install_sw
cd /usr/src
rm -rf /usr/src/openssl

mkdir -p /usr/local/openssl/etc/ssl/
curl -fSSLo /usr/local/openssl/etc/ssl/cert.pem \
    "https://raw.githubusercontent.com/certifi/python-certifi/refs/heads/master/certifi/cacert.pem"
