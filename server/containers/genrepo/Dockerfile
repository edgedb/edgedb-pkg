FROM debian:bullseye

ENV REPO_LOCAL_DIR=/var/tmp/repo/local/
ENV REPO_INCOMING_DIR=/var/spool/repo/incoming/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            openssh-server bash inoticoming gosu gnupg libffi-dev \
            gcc python3-dev python3-setuptools python3-pip python3-apt \
            reprepro createrepo-c rpm dnf awscli \
    && pip3 install boto3 \
    && pip3 install mypy-boto3-s3 \
    && pip3 install click \
    && pip3 install typing-extensions \
    && pip3 install tomli \
    && addgroup --gid 2000 repomgr \
    && adduser --uid 2000 --gid 2000 repomgr \
    && addgroup uploaders \
    && addgroup incoming \
    && adduser --ingroup uploaders \
               --home $REPO_INCOMING_DIR --no-create-home uploader \
    && adduser repomgr incoming \
    && adduser uploader incoming \
    && mkdir -p $REPO_INCOMING_DIR/triggers \
    && mkdir -p $REPO_INCOMING_DIR/linux-x86_64 \
    && mkdir -p $REPO_INCOMING_DIR/macos-x86_64 \
    && mkdir -p $REPO_INCOMING_DIR/win-x86_64 \
    && mkdir -p $REPO_INCOMING_DIR/source \
    && chown -R repomgr:incoming $REPO_INCOMING_DIR \
    && chmod g+ws $REPO_INCOMING_DIR \
    && chmod g+ws $REPO_INCOMING_DIR/linux-x86_64 \
    && chmod g+ws $REPO_INCOMING_DIR/macos-x86_64 \
    && chmod g+ws $REPO_INCOMING_DIR/win-x86_64 \
    && chmod g+ws $REPO_INCOMING_DIR/source \
    && chmod g+ws $REPO_INCOMING_DIR/triggers \
    && mkdir -p /etc/ssh/authorized_keys/ \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ \
    && mkdir -p /etc/ssh.default/ \
    && rm -rf /var/lib/apt/lists/*

COPY config/genrepo.toml /etc/genrepo.toml
COPY config/sshd/* /etc/ssh.default/
COPY config/gnupg/* /home/repomgr/.gnupg/
COPY config/rpm/rpmmacros /home/repomgr/.rpmmacros
COPY entrypoint.sh /entrypoint.sh
COPY fetch_secrets.py /usr/local/bin/
COPY process_incoming.py /usr/local/bin/
COPY visor.py /usr/local/bin/
RUN sed -i -e "s|%%REPO_INCOMING_DIR%%|${REPO_INCOMING_DIR}|g" \
        /usr/local/bin/process_incoming.py \
    && sed -i -e "s|%%REPO_LOCAL_DIR%%|${REPO_LOCAL_DIR}|g" \
        /usr/local/bin/process_incoming.py

RUN chown -R repomgr:repomgr /home/repomgr/.gnupg \
    && chmod 700 /home/repomgr/.gnupg \
    && chmod 600 /home/repomgr/.gnupg/*

EXPOSE 22

VOLUME /var/tmp/repo

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
