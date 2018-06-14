#!/bin/sh

set -ex

if [ -L "${0}" ]; then
    SCRIPT="$(readlink "${0}")"
else
    SCRIPT="${0}"
fi

DIR=$(dirname "${SCRIPT}")

for container in "${DIR}"/containers/*; do
    if ! [ -d "${container}" ]; then
        continue
    fi

    if ! [ -x "${container}/build.sh" ]; then
        continue
    fi

    "${container}/build.sh"
done
