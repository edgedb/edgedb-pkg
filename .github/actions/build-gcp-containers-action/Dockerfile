FROM debian:stretch-slim

RUN export CLOUD_SDK_REPO="cloud-sdk-stretch" \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        gnupg2 curl ca-certificates apt-transport-https \
    && echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" \
        | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | apt-key add - \
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian stretch stable" \
        | tee -a /etc/apt/sources.list.d/docker.list \
    && curl -fsSL https://download.docker.com/linux/debian/gpg \
        | apt-key add - \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        google-cloud-sdk docker-ce \
    && apt-get remove -y gnupg2 curl apt-transport-https \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
