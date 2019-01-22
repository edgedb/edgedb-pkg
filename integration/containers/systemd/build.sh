#!/bin/sh

set -ex

if [ -L "${0}" ]; then
  SCRIPT="$(readlink "${0}")"
else
  SCRIPT="${0}"
fi

DIR=$(dirname "${SCRIPT}")

for variant_dir in "${DIR}"/*; do
    if ! [ -d "${variant_dir}" ]; then
        continue
    fi

    variant=$(basename "${variant_dir}")
    image="${CI_REGISTRY_IMAGE}/systemd:${variant}"
    docker build -t "${image}" "${variant_dir}"
    docker push "${image}"
done
