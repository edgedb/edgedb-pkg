#!/usr/bin/env bash

set -e

[ "$DEBUG" == 'true' ] && set -x

chown repomgr:repomgr "${REPO_BASE_DIR}"

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

if [ "$DEBUG" == 'true' ]; then
    echo "LogLevel DEBUG2" >> "/etc/ssh.default/sshd_config"
fi

if [ -e "/root/gpg-keys/" ]; then
    while IFS= read -r -d '' path; do
        cat "${path}" | gosu repomgr:repomgr gpg --import
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

echo REPO_BASE_DIR=${REPO_BASE_DIR} >> /etc/environment
echo REPO_CONFIG_DIR=${REPO_CONFIG_DIR} >> /etc/environment


stopdaemon() {
    local pid

    echo "Received SIGINT or SIGTERM. Shutting down $1"
    # Get PID
    pid=$(cat /var/run/$1/$1.pid)
    # Set TERM
    kill -SIGTERM "${pid}"
    # Wait for exit
    wait "${pid}"
    # All done.
    echo "Done."
}

startdaemon() {
    local daemon=$1
    local pid
    local status

    shift
    $@ &
    status=$?
    pid="$!"
    mkdir -p /var/run/$daemon && echo "${pid}" > /var/run/$daemon/$daemon.pid
    return $status
}

stop() {
    stopdaemon sshd
    stopdaemon incrond
}

echo "Running $@"
if [ "$(basename $1)" == "sshd" ]; then
    if [ "$DEBUG" == 'true' ]; then
        echo "sshd_config"
        echo "-----------"
        cat "/etc/ssh.default/sshd_config"
    fi
    trap stop SIGINT SIGTERM
    startdaemon sshd $@
    startdaemon incrond incrond -n

    wait $(cat /var/run/sshd/sshd.pid)
else
    exec "$@"
fi
