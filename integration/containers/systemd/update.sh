#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

cd "$(dirname "$(readlink -f "$BASH_SOURCE")")"

generated_warning() {
	cat <<-EOH
		#
		# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
		#
		# PLEASE DO NOT EDIT IT DIRECTLY.
		#

	EOH
}

entrypoint="$(cat entrypoint.sh | sed -r -e 's/^(.*)$/\1\\n\\/g')"
entrypoint_cmd="RUN /bin/echo -e '${entrypoint}' >/usr/local/bin/entrypoint.sh"

tmp=$(mktemp /tmp/dockerfile-update.XXXXXX)
echo "${entrypoint_cmd}" >"${tmp}"

while IFS= read -r -d '' v; do
	dir="${v}"
	variant="$(basename "${v}")"

	case "$variant" in
		ubuntu*) template='ubuntu'; tag="${variant}" ;;
		debian*) template='debian'; tag="${variant}" ;;
		fedora*) template='fedora'; tag="${variant}" ;;
		centos*) template='centos'; tag="${variant}" ;;
		*) echo "Unsupported variant: ${variant}" >@2; exit 1 ;;
	esac

	template="Dockerfile-${template}.template"

	{ generated_warning; cat "$template"; } > "$dir/Dockerfile"

	sed -ri \
		-e 's!^(FROM (\w+)):.*!\1:'"${variant#*-}"'!'\
		"$dir/Dockerfile"

	awk -i inplace '@load "readfile"; BEGIN{l = readfile("'"${tmp}"'")}/%%WRITE_ENTRYPOINT%/{gsub("%%WRITE_ENTRYPOINT%%", l)}1' "${dir}/Dockerfile"

done < <(find . -maxdepth 1 -type d -name '*-*' -print0)

rm "${tmp}"
