#!/bin/sh

set -ex

if [ -L "${0}" ]; then
  SCRIPT="$(readlink "${0}")"
else
  SCRIPT="${0}"
fi

DIR=$(dirname "${SCRIPT}")

for version_dir in "${DIR}"/*; do
    if ! [ -d "${version_dir}" ]; then
        continue
    fi

	VERSION=$(basename "${version_dir}")

	for variant_dir in "${version_dir}"/*; do
        if ! [ -d "${variant_dir}" ]; then
            continue
        fi

	    VARIANT=$(basename "${variant_dir}")

		case "${VARIANT}" in
			ubuntu*) tag="${VARIANT#*-}" ;;
			*) tag="${VARIANT}" ;;
		esac

		image="${CI_REGISTRY_IMAGE}/python:${VERSION}-${tag}"
		docker build -t "${image}" "${variant_dir}"
		# docker push "${image}"
	done
done
