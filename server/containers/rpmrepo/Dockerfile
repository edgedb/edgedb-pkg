FROM centos:7

ENV REPO_BASE_DIR=/var/lib/repos/
ENV REPO_INCOMING_DIR=/var/spool/repo/incoming/

RUN yum install -y \
        https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
    && yum install -y \
        createrepo openssh-server bash incron sudo gnupg rpm-sign \
    && groupadd --gid 2000 repomgr \
    && useradd --uid 2000 --gid 2000 repomgr \
    && groupadd uploaders \
    && groupadd incoming \
    && useradd -G uploaders -d $REPO_INCOMING_DIR --no-create-home uploader \
    && gpasswd -a repomgr incoming \
    && gpasswd -a uploader incoming \
    && mkdir -p $REPO_INCOMING_DIR \
    && chown repomgr:incoming $REPO_INCOMING_DIR \
    && chmod g+ws $REPO_INCOMING_DIR \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ \
    && mkdir -p /etc/ssh.default/ \
    && rm -rf /var/lib/apt/lists/*

COPY config/sshd/* /etc/ssh.default/
COPY config/gnupg/* /home/repomgr/.gnupg/
COPY config/rpm/rpmmacros /home/repomgr/.rpmmacros
COPY config/incron/incron.allow /etc/
COPY config/incron/incrontab /var/spool/incron/repomgr
COPY entrypoint.sh /entrypoint.sh
COPY processincoming.sh /usr/local/bin/

RUN chown -R repomgr:repomgr /home/repomgr/.gnupg \
    && chmod 700 /home/repomgr/.gnupg \
    && chmod 600 /home/repomgr/.gnupg/* \
    && chmod 600 /var/spool/incron/repomgr

EXPOSE 22

VOLUME $REPO_BASE_DIR

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
