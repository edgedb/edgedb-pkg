#!/bin/sh

set -e

# https://cloud.google.com/sdk/gcloud/reference/auth/activate-service-account
printf "%s" "${GCP_SERVICE_KEY}" > "${HOME}/.gcpkey.json"
gcloud auth activate-service-account \
    "${GCP_SERVICE_ACCOUNT}" --key-file="${HOME}/.gcpkey.json"

gcloud auth configure-docker

set -ex

containers="$(dirname $0)/containers/"

for container in $(ls "${containers}"); do
    repo="gcr.io/edgedb-infra/${container}"
    tag="latest"
    docker build -t "${repo}:${tag}" "${containers}/${container}"
    docker push "${repo}"
done
