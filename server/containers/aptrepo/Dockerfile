FROM debian:stretch-slim

ENV REPREPRO_BASE_DIR=/var/lib/repos/
ENV REPREPRO_CONFIG_DIR=/etc/reprepro/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            reprepro \
    && rm -rf /var/lib/apt/lists/*

COPY config/* /etc/reprepro/
COPY entrypoint.sh /entrypoint.sh

VOLUME $REPREPRO_BASE_DIR

ENTRYPOINT ["/entrypoint.sh"]
