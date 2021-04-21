#!/usr/bin/env bash

set -e

[ "$DEBUG" == 'true' ] && set -x

mkdir -p "${REPO_LOCAL_DIR}"
chown -R repomgr:repomgr "${REPO_LOCAL_DIR}"
chmod -R g+ws "${REPO_LOCAL_DIR}"

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
    SSH_KEY_WILDCARD="server-host-key-*"
elif ls /etc/ssh/ssh_host_* 1> /dev/null 2>&1; then
    echo "Found custom ssh host keys in /etc/ssh/"
    SSH_KEY_WILDCARD="ssh_host_*_key"
else
    echo "No ssh host keys found in /etc/ssh.  Generating."
    ssh-keygen -A
    SSH_KEY_WILDCARD="ssh_host_*_key"
fi

find /etc/ssh -name $SSH_KEY_WILDCARD

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
        cat "${path}" | gosu repomgr:repomgr gpg --import
    done < <(find "/root/gpg-keys/" -maxdepth 1 -type f -print0)
fi

if [ "${AWS_ACCESS_KEY_ID}" != "" ]; then
    mkdir -p /home/repomgr/.aws
    echo "[default]" >/home/repomgr/.aws/credentials
    echo "aws_access_key_id = ${AWS_ACCESS_KEY_ID}" >>/home/repomgr/.aws/credentials
    echo "aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}" >>/home/repomgr/.aws/credentials
    chown -R repomgr:repomgr /home/repomgr/.aws
    chmod 400 /home/repomgr/.aws/credentials
fi

gosu repomgr:repomgr aws s3 sync --delete s3://edgedb-packages/rpm/ "${REPO_LOCAL_DIR}/"

if [ -n "${PORT}" ]; then
    echo "Port ${PORT}" >> "/etc/ssh.default/sshd_config"
else
    echo "Port 22" >> "/etc/ssh.default/sshd_config"
fi

# Conditional blocks go last
cat "/etc/ssh.default/sshd_config_conditional" >> \
    "/etc/ssh.default/sshd_config"

mkdir -p /var/run/sshd

if [ "$(basename $1)" == "sshd" ]; then
    if [ "$DEBUG" == 'true' ]; then
        echo "sshd_config"
        echo "-----------"
        cat "/etc/ssh.default/sshd_config"
    fi
    rm /run/nologin
    export PYTHONUNBUFFERED=1
    /usr/local/bin/visor.py << EOF
        [sshd]
        cmd = $@
        [inoticoming]
        user = repomgr
        cmd =
            inoticoming
            --initialsearch
            --foreground
            ${REPO_INCOMING_DIR}/triggers/
            --chdir
            ${REPO_INCOMING_DIR}
            /usr/local/bin/processincoming.sh
            triggers/{}
            \;
EOF
else
    exec "$@"
fi
