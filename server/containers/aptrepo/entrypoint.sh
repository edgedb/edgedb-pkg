#!/usr/bin/env bash

set -e

[ "$DEBUG" == 'true' ] && set -x

DAEMON=sshd


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

if [ -e "/etc/ssh/sshd_config" ]; then
    cat "/etc/ssh/sshd_config" >> "/etc/ssh.default/sshd_config"
fi

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
    trap stop SIGINT SIGTERM
    $@ &
    pid="$!"
    mkdir -p /var/run/$DAEMON && echo "${pid}" > /var/run/$DAEMON/$DAEMON.pid
    wait "${pid}" && exit $?
else
    exec "$@"
fi
