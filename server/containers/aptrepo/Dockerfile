FROM debian:buster

ENV REPREPRO_BASE_DIR=/var/tmp/repo/local/
ENV REPREPRO_CONFIG_DIR=/etc/reprepro/
ENV REPREPRO_SPOOL_DIR=/var/spool/reprepro
ENV REPREPRO_INCOMING_TMP_DIR=/var/tmp/incoming-staging/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            reprepro openssh-server bash inoticoming gosu gnupg \
            gcc python3-dev python3-setuptools python3-pip libffi-dev \
    && pip3 install gsutil \
    && addgroup --gid 2000 reprepro \
    && adduser --uid 2000 --gid 2000 reprepro \
    && addgroup uploaders \
    && addgroup incoming \
    && adduser --ingroup uploaders \
               --home $REPREPRO_SPOOL_DIR --no-create-home uploader \
    && adduser reprepro incoming \
    && adduser uploader incoming \
    && mkdir -p $REPREPRO_SPOOL_DIR/incoming \
    && chown reprepro:incoming $REPREPRO_SPOOL_DIR/incoming \
    && chmod g+ws $REPREPRO_SPOOL_DIR/incoming \
    && mkdir -p $REPREPRO_INCOMING_TMP_DIR \
    && chown reprepro:reprepro $REPREPRO_INCOMING_TMP_DIR \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ \
    && mkdir -p /etc/ssh.default/ \
    && rm -rf /var/lib/apt/lists/*

COPY config/reprepro/* /etc/reprepro/
COPY config/sshd/* /etc/ssh.default/
COPY config/gnupg/* /home/reprepro/.gnupg/
COPY entrypoint.sh /entrypoint.sh
COPY processincoming.sh /usr/local/bin/
COPY makeindex.py /usr/local/bin/

RUN chown -R reprepro:reprepro /home/reprepro/.gnupg \
    && chmod 700 /home/reprepro/.gnupg \
    && chmod 600 /home/reprepro/.gnupg/*

VOLUME /var/tmp/repo

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
