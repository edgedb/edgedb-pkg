FROM debian:stretch-slim

ENV REPREPRO_BASE_DIR=/var/lib/repos/
ENV REPREPRO_CONFIG_DIR=/etc/reprepro/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            reprepro openssh-server bash \
    && addgroup --system --gid 700 reprepro \
    && adduser --system --uid 700 --gid 700 reprepro \
    && addgroup uploaders \
    && adduser --ingroup uploaders uploader \
    && adduser reprepro uploaders \
    && mkdir -p /var/tmp/incoming/ \
    && chown reprepro:uploaders /var/tmp/incoming \
    && chmod g+ws /var/tmp/incoming/ \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ && \
    && mkdir -p /etc/ssh.default/ && \
    && rm -rf /var/lib/apt/lists/*

COPY config/reprepro/* /etc/reprepro/
COPY config/sshd/* /etc/ssh.default/
COPY entrypoint.sh /entrypoint.sh

EXPOSE 22

VOLUME $REPREPRO_BASE_DIR

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
