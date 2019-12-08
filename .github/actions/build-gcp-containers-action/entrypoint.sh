#!/bin/bash

set -Eeo pipefail

# https://cloud.google.com/sdk/gcloud/reference/auth/activate-service-account
printf "%s" "${INPUT_GCP_SERVICE_KEY}" > "${HOME}/.gcpkey.json"
gcloud auth activate-service-account \
    "${INPUT_GCP_SERVICE_ACCOUNT}" --key-file="${HOME}/.gcpkey.json"

gcloud auth configure-docker

set -Exeo pipefail

for container in $(ls "${INPUT_PATH}"); do
    if [ ! -d "${INPUT_PATH}/${container}" ]; then
        continue
    fi

    repo="gcr.io/edgedb-infra/${container}"
    tag="latest"
    docker build -t "${repo}:${tag}" "${INPUT_PATH}/${container}"
    docker push "${repo}"
done
