#!/usr/bin/env bash

set -e

[ "$DEBUG" == 'true' ] && set -x

echo REPREPRO_CONFIG_DIR=${REPREPRO_CONFIG_DIR} >> /etc/environment

mkdir -p "${REPREPRO_BASE_DIR}"
chown -R reprepro:reprepro "${REPREPRO_BASE_DIR}"

if [ -w ~/.ssh ]; then
    chown root:root ~/.ssh && chmod 700 ~/.ssh/
fi

fetch_secrets.py client-keys-root /root/.ssh -f authorized_keys
fetch_secrets.py client-keys-uploaders /etc/ssh/authorized_keys -f uploaders

if [ -w ~/.ssh/authorized_keys ]; then
    chown root:root ~/.ssh/authorized_keys
    chmod 400 ~/.ssh/authorized_keys
fi

fetch_secrets.py server-host-key- /etc/ssh/

if ls /etc/ssh/server-host-key-* 1> /dev/null 2>&1; then
    echo "Found shared ssh host keys in /etc/ssh/"
    SSH_KEY_WILDCARD="'server-host-key-*'"
elif ls /etc/ssh/ssh_host_* 1> /dev/null 2>&1; then
    echo "Found custom ssh host keys in /etc/ssh/"
    SSH_KEY_WILDCARD="'ssh_host_*_key'"
else
    echo "No ssh host keys found in /etc/ssh.  Generating."
    ssh-keygen -A
    SSH_KEY_WILDCARD="'ssh_host_*_key'"
fi

if [ "$DEBUG" == 'true' ]; then
    echo "sshd_config"
    echo "-----------"
    cat "/etc/ssh.default/sshd_config"
fi

while IFS= read -r -d '' path; do
    echo HostKey "${path}" >> "/etc/ssh.default/sshd_config"
    if [ -w "${path}" ]; then
        chown root:root "${path}"
        chmod 400 "${path}"
    fi
done < <(find "/etc/ssh/" -name $SSH_KEY_WILDCARD -print0)

if [ "$DEBUG" == 'true' ]; then
    echo "LogLevel DEBUG2" >> "/etc/ssh.default/sshd_config"
fi

fetch_secrets.py release-signing- /root/gpg-keys/

if [ -e "/root/gpg-keys/" ]; then
    while IFS= read -r -d '' path; do
        cat "${path}" | gosu reprepro:reprepro gpg --import
    done < <(find "/root/gpg-keys/" -maxdepth 1 -type f -print0)
fi

chown -R reprepro:reprepro "${REPREPRO_BASE_DIR}"

mkdir -p /home/reprepro/.aws
echo "[default]" >/home/reprepro/.aws/credentials
echo "aws_access_key_id = ${AWS_ACCESS_KEY_ID}" >>/home/reprepro/.aws/credentials
echo "aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}" >>/home/reprepro/.aws/credentials
chown -R reprepro:reprepro /home/reprepro/.aws
chmod 400 /home/reprepro/.aws/credentials

if [ -n "${PORT}" ]; then
    echo "Port ${PORT}" >> "/etc/ssh.default/sshd_config"
else
    echo "Port 22" >> "/etc/ssh.default/sshd_config"
fi

# Conditional blocks go last
cat "/etc/ssh.default/sshd_config_conditional" >> \
    "/etc/ssh.default/sshd_config"

DAEMON=sshd

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
    mkfifo ${DAEMON}_pipe
    $@ &>${DAEMON}_pipe &
    pid="$!"
    mkdir -p /var/run/$DAEMON && echo "${pid}" > /var/run/$DAEMON/$DAEMON.pid
    grep -v "Did not receive identification string from" <${DAEMON}_pipe &

    gosu reprepro:reprepro \
        inoticoming --initialsearch --foreground \
            "${REPREPRO_SPOOL_DIR}/incoming" \
            --suffix '.changes' \
            --chdir "${REPREPRO_SPOOL_DIR}" \
            /usr/local/bin/processincoming.sh {} \;
else
    exec "$@"
fi
