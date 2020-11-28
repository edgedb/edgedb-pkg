FROM centos:8

ENV REPO_LOCAL_DIR=/var/tmp/repo/local/
ENV REPO_INCOMING_DIR=/var/spool/repo/incoming/

RUN yum install -y \
        https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm \
    && yum install -y \
        createrepo openssh-server bash gnupg rpm-sign wget \
        yum-utils gcc gcc-c++ make python38 python38-devel libffi-devel \
    && pip3.8 install boto3 awscli click \
    && groupadd --gid 2000 repomgr \
    && useradd --uid 2000 --gid 2000 repomgr \
    && groupadd uploaders \
    && groupadd incoming \
    && useradd -G uploaders -d $REPO_INCOMING_DIR --no-create-home uploader \
    && gpasswd -a repomgr incoming \
    && gpasswd -a uploader incoming \
    && mkdir -p $REPO_INCOMING_DIR/triggers \
    && chown -R repomgr:incoming $REPO_INCOMING_DIR \
    && chmod -R g+ws $REPO_INCOMING_DIR \
    && mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ \
    && mkdir -p /etc/ssh.default/

RUN wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/1.12/gosu-amd64" \
    && chmod +x /usr/local/bin/gosu \
    && gosu --version \
    && cd /tmp/ \
    && wget https://salsa.debian.org/brlink/inoticoming/-/archive/debian/inoticoming-debian.tar.gz \
    && tar xzvf inoticoming-debian.tar.gz \
    && cd /tmp/inoticoming-debian \
    && ./configure && make install \
    && cd /tmp/ \
    && rm -rf inoticoming-debian inoticoming-debian.tar.gz \
    && inoticoming --version

COPY config/sshd/* /etc/ssh.default/
COPY config/gnupg/* /home/repomgr/.gnupg/
COPY config/rpm/rpmmacros /home/repomgr/.rpmmacros
COPY entrypoint.sh /entrypoint.sh
COPY fetch_secrets.py /usr/local/bin/
COPY remove_old_dev_pkg.py /usr/local/bin/
COPY processincoming.sh /usr/local/bin/
COPY makeindex.py /usr/local/bin/
COPY visor.py /usr/local/bin/
RUN sed -i -e "s|%%REPO_INCOMING_DIR%%|${REPO_INCOMING_DIR}|g" \
        /usr/local/bin/processincoming.sh \
    && sed -i -e "s|%%REPO_LOCAL_DIR%%|${REPO_LOCAL_DIR}|g" \
        /usr/local/bin/processincoming.sh

RUN chown -R repomgr:repomgr /home/repomgr/.gnupg \
    && chmod 700 /home/repomgr/.gnupg \
    && chmod 600 /home/repomgr/.gnupg/*

EXPOSE 22

VOLUME /var/tmp/repo

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
