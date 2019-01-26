FROM docker.io/alpine:3.6

RUN apk update && \
    apk add bash openssh && \
    deluser $(getent passwd 33 | cut -d: -f1) && \
    delgroup $(getent group 33 | cut -d: -f1) 2>/dev/null || true && \
    mkdir -p ~root/.ssh && chmod 700 ~root/.ssh/ && \
    mkdir -p /etc/ssh.default/ && \
    echo -e "Port 22\nStrictModes no\n" >> /etc/ssh.default/sshd_config && \
    rm -rf /var/cache/apk/*

EXPOSE 22

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/sbin/sshd", "-e", "-D", "-f", "/etc/ssh.default/sshd_config"]
