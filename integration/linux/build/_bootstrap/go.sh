#!/usr/bin/env bash

set -ex

: ${GO_VERSION:=1.23.1}

case "$(arch)" in
    x86_64)
        GO_ARCH='amd64'
        ;;
    arm64)
        GO_ARCH='arm64'
        ;;
    aarch64)
        GO_ARCH='arm64'
        ;;
    *)
        echo "unsupported architecture"
        exit 1
        ;;
esac

cd /usr/src
curl --proto '=https' --tlsv1.2 -sSfL \
	"https://go.dev/dl/go${GO_VERSION}.linux-${GO_ARCH}.tar.gz" -o go.tgz

tar -C /usr/local -xzf go.tgz
rm go.tgz
