function fetch_keys() {
    for key in "${@}"; do
        gpg --batch --keyserver pgp.mit.edu --recv-keys "$key" \
        || gpg --batch --keyserver keyserver.pgp.com --recv-keys "$key" \
        || gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key" \
        || gpg --batch --keyserver keys.openpgp.org --recv-keys "$key"
    done
}
