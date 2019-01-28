FROM debian:stretch-slim

ENV REPREPRO_BASE_DIR=/var/lib/repos/
ENV REPREPRO_CONFIG_DIR=/etc/reprepro/
ENV REPREPRO_INCOMING_DIR=/var/spool/reprepro/incoming/
ENV REPREPRO_INCOMING_TMP_DIR=/var/tmp/incoming-staging/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            reprepro openssh-server bash inoticoming gosu gnupg \
    && addgroup --gid 999 reprepro \
    && adduser --uid 999 --gid 999 reprepro \
    && addgroup uploaders \
    && addgroup incoming \
    && adduser --ingroup uploaders \
               --home $REPREPRO_INCOMING_DIR --no-create-home uploader \
    && adduser reprepro incoming \
    && adduser uploader incoming \
    && mkdir -p $REPREPRO_INCOMING_DIR \
    && chown reprepro:incoming $REPREPRO_INCOMING_DIR \
    && chmod g+ws $REPREPRO_INCOMING_DIR \
    && mkdir -p $REPREPRO_INCOMING_TMP_DIR \
    && chown reprepro:reprepro $REPREPRO_INCOMING_TMP_DIR \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ \
    && mkdir -p /etc/ssh.default/ \
    && rm -rf /var/lib/apt/lists/*

COPY config/reprepro/* /etc/reprepro/
COPY config/sshd/* /etc/ssh.default/
COPY conifg/gnupg/* /home/reprepro/.gnupg/
COPY entrypoint.sh /entrypoint.sh

EXPOSE 22

VOLUME $REPREPRO_BASE_DIR

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
