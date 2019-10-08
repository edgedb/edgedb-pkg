#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

declare -A gpgKeys=(
	# gpg: key 18ADD4FF: public key "Benjamin Peterson <benjamin@python.org>" imported
	[2.7]='C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF'
	# https://www.python.org/dev/peps/pep-0373/#release-manager-and-crew

	# gpg: key F73C700D: public key "Larry Hastings <larry@hastings.org>" imported
	[3.4]='97FC712E4C024BBEA48A61ED3A5CA953F73C700D'
	# https://www.python.org/dev/peps/pep-0429/#release-manager-and-crew

	# gpg: key F73C700D: public key "Larry Hastings <larry@hastings.org>" imported
	[3.5]='97FC712E4C024BBEA48A61ED3A5CA953F73C700D'
	# https://www.python.org/dev/peps/pep-0478/#release-manager-and-crew

	# gpg: key AA65421D: public key "Ned Deily (Python release signing key) <nad@acm.org>" imported
	[3.6]='0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D'
	# https://www.python.org/dev/peps/pep-0494/#release-manager-and-crew

	# gpg: key AA65421D: public key "Ned Deily (Python release signing key) <nad@acm.org>" imported
	[3.7]='0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D'
	# https://www.python.org/dev/peps/pep-0494/#release-manager-and-crew
)

cd "$(dirname "$(readlink -f "$BASH_SOURCE")")"

version="3.7"
pipVersion="$(curl -fsSL 'https://pypi.org/pypi/pip/json' | jq -r .info.version)"

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
entrypoint_cmd="RUN /bin/echo -e '${entrypoint}' >/entrypoint.sh"

tmp=$(mktemp /tmp/dockerfile-update.XXXXXX)
echo "${entrypoint_cmd}" >"${tmp}"

rcVersion="${version%-rc}"
rcGrepV='-v'
if [ "$rcVersion" != "$version" ]; then
	rcGrepV=
fi

possibles=( $(
	{
		git ls-remote --tags https://github.com/python/cpython.git "refs/tags/v${rcVersion}.*" \
			| sed -r 's!^.*refs/tags/v([0-9a-z.]+).*$!\1!' \
			| grep $rcGrepV -E -- '[a-zA-Z]+' \
			|| :

		# this page has a very aggressive varnish cache in front of it, which is why we also scrape tags from GitHub
		curl -fsSL 'https://www.python.org/ftp/python/' \
			| grep '<a href="'"$rcVersion." \
			| sed -r 's!.*<a href="([^"/]+)/?".*!\1!' \
			| grep $rcGrepV -E -- '[a-zA-Z]+' \
			|| :
	} | sort -ruV
) )
fullVersion=
declare -A impossible=()
for possible in "${possibles[@]}"; do
	rcPossible="${possible%[a-z]*}"

	# varnish is great until it isn't
	if wget -q -O /dev/null -o /dev/null --spider "https://www.python.org/ftp/python/$rcPossible/Python-$possible.tar.xz"; then
		fullVersion="$possible"
		break
	fi

	if [ -n "${impossible[$rcPossible]:-}" ]; then
		continue
	fi
	impossible[$rcPossible]=1
	possibleVersions=( $(
		wget -qO- -o /dev/null "https://www.python.org/ftp/python/$rcPossible/" \
			| grep '<a href="Python-'"$rcVersion"'.*\.tar\.xz"' \
			| sed -r 's!.*<a href="Python-([^"/]+)\.tar\.xz".*!\1!' \
			| grep $rcGrepV -E -- '[a-zA-Z]+' \
			| sort -rV \
			|| true
	) )
	if [ "${#possibleVersions[@]}" -gt 0 ]; then
		fullVersion="${possibleVersions[0]}"
		break
	fi
done

if [ -z "$fullVersion" ]; then
	{
		echo
		echo
		echo "  error: cannot find $version (alpha/beta/rc?)"
		echo
		echo
	} >&2
	exit 1
fi

echo "$version: $fullVersion"

while IFS= read -r -d '' v; do
	dir="$v"
	variant="$(basename "$v")"

	[ -d "$dir" ] || continue

	case "$variant" in
		ubuntu*) template='ubuntu'; tag="${variant}" ;;
		centos*) template='centos'; tag="${variant}" ;;
		fedora*) template='fedora'; tag="${variant}" ;;
		debian*) template='debian'; tag="${variant}" ;;
	esac

	template="Dockerfile-${template}.template"

	{ generated_warning; cat "$template"; } > "$dir/Dockerfile"

	sed -ri \
		-e 's/^(ENV GPG_KEY) .*/\1 '"${gpgKeys[$version]:-${gpgKeys[$rcVersion]}}"'/' \
		-e 's/^(ENV PYTHON_VERSION) .*/\1 '"$fullVersion"'/' \
		-e 's/^(ENV PYTHON_RELEASE) .*/\1 '"${fullVersion%%[a-z]*}"'/' \
		-e 's/^(ENV PYTHON_PIP_VERSION) .*/\1 '"$pipVersion"'/' \
		-e 's!^(FROM (buildpack-deps)):.*!\1:'"${variant#*-}"'!' \
		-e 's!^(FROM (\w+)):.*!\1:'"${variant#*-}"'!'\
		"$dir/Dockerfile"

	case "$version/$v" in
		*/stretch)
			sed -ri -e '/libssl-dev/d' "$dir/Dockerfile"
			;;
	esac

	awk -i inplace '@load "readfile"; BEGIN{l = readfile("'"${tmp}"'")}/%%WRITE_ENTRYPOINT%/{gsub("%%WRITE_ENTRYPOINT%%", l)}1' "${dir}/Dockerfile"

done < <(find . -maxdepth 1 -type d -name '*-*' -print0)
