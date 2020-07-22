FROM debian:buster

ENV REPO_LOCAL_DIR=/var/spool/repo/local/
ENV REPO_INCOMING_DIR=/var/spool/repo/incoming/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            openssh-server bash incron sudo gnupg \
            gcc python3-dev python3-setuptools python3-pip libffi-dev \
    && pip3 install gsutil \
    && addgroup --gid 2000 repomgr \
    && adduser --uid 2000 --gid 2000 repomgr \
    && addgroup uploaders \
    && addgroup incoming \
    && adduser --ingroup uploaders \
               --home $REPO_INCOMING_DIR --no-create-home uploader \
    && adduser repomgr incoming \
    && adduser uploader incoming \
    && mkdir -p $REPO_LOCAL_DIR \
    && chown -R repomgr:repomgr $REPO_LOCAL_DIR \
    && chmod -R g+ws $REPO_LOCAL_DIR \
    && mkdir -p $REPO_INCOMING_DIR/triggers \
    && mkdir -p $REPO_INCOMING_DIR/macos \
    && mkdir -p $REPO_INCOMING_DIR/source \
    && chown -R repomgr:incoming $REPO_INCOMING_DIR \
    && chmod g+ws $REPO_INCOMING_DIR \
    && chmod g+ws $REPO_INCOMING_DIR/macos \
    && chmod g+ws $REPO_INCOMING_DIR/source \
    && chmod g+ws $REPO_INCOMING_DIR/triggers \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ \
    && mkdir -p /etc/ssh.default/ \
    && rm -rf /var/lib/apt/lists/*

COPY config/sshd/* /etc/ssh.default/
COPY config/gnupg/* /home/repomgr/.gnupg/
COPY config/incron/incron.allow /etc/
COPY config/incron/incrontab /var/spool/incron/repomgr
COPY entrypoint.sh /entrypoint.sh
COPY processincoming.sh /usr/local/bin/
COPY makeindex.py /usr/local/bin/
COPY findold.py /usr/local/bin/
RUN sed -i -e "s|%%REPO_INCOMING_DIR%%|${REPO_INCOMING_DIR}|g" \
        /usr/local/bin/processincoming.sh \
    && sed -i -e "s|%%REPO_LOCAL_DIR%%|${REPO_LOCAL_DIR}|g" \
        /usr/local/bin/processincoming.sh

RUN chown -R repomgr:repomgr /home/repomgr/.gnupg \
    && chmod 700 /home/repomgr/.gnupg \
    && chmod 600 /home/repomgr/.gnupg/* \
    && chmod 600 /var/spool/incron/repomgr

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
