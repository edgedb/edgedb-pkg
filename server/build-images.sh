#!/bin/sh

set -e

if [ -z ${AWS_ACCOUNT+x} ]; then
    echo "Set \$AWS_ACCOUNT to use this."
    exit 1
fi

AWS_URL="${AWS_ACCOUNT}.dkr.ecr.us-east-2.amazonaws.com"

# Requires local credentials to be present or the use of the
# aws-actions/configure-aws-credentials@v1 GitHub action.
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $AWS_URL

set -ex

containers="$(dirname $0)/containers/"

for container in $(ls "${containers}"); do
    repo="${AWS_URL}/${container}"
    tag="latest"
    docker build -t "${repo}:${tag}" "${containers}/${container}"
    docker push "${repo}"
done
