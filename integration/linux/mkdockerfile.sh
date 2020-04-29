#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

generated_warning() {
	cat <<-EOH
		#
		# NOTE: THIS DOCKERFILE IS GENERATED VIA "mkdockerfile.sh"
		#
		# PLEASE DO NOT EDIT IT DIRECTLY.
		#

	EOH
}

template="${1}"
target="${2}"
variant="$(dirname ${target})"
platform="${variant%%-*}"

{ generated_warning; cat "$template"; } > "${target}"

sed -ri \
	-e 's!^(FROM (\w+)):%%PLACEHOLDER%%!\1:'"${variant#*-}"'!'\
	"${target}"

entrypoint="$(cat entrypoint-${platform}.sh \
				| sed -r -e 's/\\/\\\\/g' \
				| sed -r -e 's/\x27/\x27\\\x27\x27/g' \
				| sed -r -e 's/^(.*)$/\1\\n\\/g' \
				| sed -r -e 's/&/\\&/g')"
entrypoint_cmd="RUN /bin/echo -e '${entrypoint}' >/entrypoint.sh"

tmp=$(mktemp /tmp/mkdockerfile.XXXXXX)
echo "${entrypoint_cmd}" >"${tmp}"
awk -i inplace '@load "readfile"; BEGIN{l = readfile("'"${tmp}"'")}/%%WRITE_ENTRYPOINT%%/{gsub("%%WRITE_ENTRYPOINT%%", l)}1' "${target}"
rm "${tmp}"
