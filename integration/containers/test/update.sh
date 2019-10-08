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

while IFS= read -r -d '' v; do
	dir="${v}"
	variant="$(basename "${v}")"

	case "$variant" in
		ubuntu*) platform='ubuntu'; tag="${variant}" ;;
		debian*) platform='debian'; tag="${variant}" ;;
		centos*) platform='centos'; tag="${variant}" ;;
		*) echo "Unsupported variant: ${variant}" >@2; exit 1 ;;
	esac

	template="Dockerfile-${platform}.template"

	{ generated_warning; cat "$template"; } > "$dir/Dockerfile"

	sed -ri \
		-e 's!^(FROM (\w+)):.*!\1:'"${variant#*-}"'!'\
		"$dir/Dockerfile"

	entrypoint="$(cat entrypoint-${platform}.sh | sed -r -e 's/\\/\\\\/g' | sed -r -e 's/^(.*)$/\1\\n\\/g')"
	entrypoint_cmd="RUN /bin/echo -e '${entrypoint}' >/entrypoint.sh"

	tmp=$(mktemp /tmp/dockerfile-update.XXXXXX)
	echo "${entrypoint_cmd}" >"${tmp}"

	awk -i inplace '@load "readfile"; BEGIN{l = readfile("'"${tmp}"'")}/%%WRITE_ENTRYPOINT%/{gsub("%%WRITE_ENTRYPOINT%%", l)}1' "${dir}/Dockerfile"

done < <(find . -maxdepth 1 -type d -name '*-*' -print0)
