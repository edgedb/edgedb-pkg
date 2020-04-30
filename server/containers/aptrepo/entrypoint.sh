#!/usr/bin/env bash

set -e

[ "$DEBUG" == 'true' ] && set -x

DAEMON=sshd

chown reprepro:reprepro "${REPREPRO_BASE_DIR}"

if [ -w ~/.ssh ]; then
    chown root:root ~/.ssh && chmod 700 ~/.ssh/
fi

if [ -w ~/.ssh/authorized_keys ]; then
    chown root:root ~/.ssh/authorized_keys
    chmod 400 ~/.ssh/authorized_keys
fi

if ls /etc/ssh/ssh_host_* 1> /dev/null 2>&1; then
    echo "Found ssh host keys in /etc/ssh/"
else
    echo "No ssh host keys found in /etc/ssh.  Generating."
    ssh-keygen -A
fi

while IFS= read -r -d '' path; do
    echo HostKey "${path}" >> "/etc/ssh.default/sshd_config"
    if [ -w "${path}" ]; then
        chown root:root "${path}"
        chmod 400 "${path}"
    fi
done < <(find "/etc/ssh/" -name 'ssh_host_*_key' -print0)

if [ -e "/root/storage-credentials/service-account-key.json" ]; then
    cp "/root/storage-credentials/service-account-key.json" \
        "/home/repomgr/.service-account-key.json"
    chown repomgr:repomgr "/home/repomgr/.service-account-key.json"
    chmod 600 "/home/repomgr/.service-account-key.json"
    cat >"/home/repomgr/.boto" <<EOF
[Credentials]
gs_service_key_file = /home/repomgr/.service-account-key.json
EOF
fi

if [ "$DEBUG" == 'true' ]; then
    echo "LogLevel DEBUG2" >> "/etc/ssh.default/sshd_config"
fi

if [ -e "/etc/ssh/sshd_config" ]; then
    cat "/etc/ssh/sshd_config" >> "/etc/ssh.default/sshd_config"
fi

if [ -e "/root/gpg-keys/" ]; then
    while IFS= read -r -d '' path; do
        cat "${path}" | gosu reprepro:reprepro gpg --import
    done < <(find "/root/gpg-keys/" -name '*.asc' -print0)
fi

if [ -n "${PORT}" ]; then
    echo "Port ${PORT}" >> "/etc/ssh.default/sshd_config"
else
    echo "Port 22" >> "/etc/ssh.default/sshd_config"
fi

# Conditional blocks go last
cat "/etc/ssh.default/sshd_config_conditional" >> \
    "/etc/ssh.default/sshd_config"

echo REPREPRO_BASE_DIR=${REPREPRO_BASE_DIR} >> /etc/environment
echo REPREPRO_CONFIG_DIR=${REPREPRO_CONFIG_DIR} >> /etc/environment


stop() {
    echo "Received SIGINT or SIGTERM. Shutting down $DAEMON"
    # Get PID
    pid=$(cat /var/run/$DAEMON/$DAEMON.pid)
    # Set TERM
    kill -SIGTERM "${pid}"
    # Wait for exit
    wait "${pid}"
    # All done.
    echo "Done."
}

echo "Running $@"
if [ "$(basename $1)" == "$DAEMON" ]; then
    if [ "$DEBUG" == 'true' ]; then
        echo "sshd_config"
        echo "-----------"
        cat "/etc/ssh.default/sshd_config"
    fi
    trap stop SIGINT SIGTERM
    $@ &
    pid="$!"
    mkdir -p /var/run/$DAEMON && echo "${pid}" > /var/run/$DAEMON/$DAEMON.pid

    gosu reprepro:reprepro \
        inoticoming --initialsearch --foreground \
            "${REPREPRO_INCOMING_DIR}" \
            --suffix '.changes' \
            --chdir "${REPREPRO_INCOMING_DIR}" \
            reprepro -v -v --waitforlock 100 processincoming main {} \;
else
    exec "$@"
fi
