#!/usr/bin/env bash
#
# Copyright (c) 2014-2015 Docker, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

set -Eeuo pipefail
shopt -s nullglob

declare -A gpgKeys=(
	[3.8]='E3FF2839C048B25C084DEBE9B26995E310250568'
)

cd "$(dirname "$(readlink -f "$BASH_SOURCE")")"

version="3.8"
pipVersion="$(curl -fsSL 'https://pypi.org/pypi/pip/json' | jq -r .info.version)"
rustVersion="1.41.1"

generated_warning() {
	cat <<-EOH
		#
		# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.sh"
		#
		# PLEASE DO NOT EDIT IT DIRECTLY.
		#

	EOH
}

entrypoint="$(cat entrypoint.sh \
				| sed -r -e 's/\\/\\\\/g' \
				| sed -r -e 's/\x27/\x27\\\x27\x27/g' \
				| sed -r -e 's/^(.*)$/\1\\n\\/g' \
				| sed -r -e 's/&/\\&/g')"
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

template="${1}"
target="${2}"
variant="$(dirname ${target})"

{ generated_warning; cat "${template}"; } > "${target}"

sed -ri \
	-e 's/^(ENV GPG_KEY) .*/\1 '"${gpgKeys[$version]:-${gpgKeys[$rcVersion]}}"'/' \
	-e 's/^(ENV PYTHON_VERSION) .*/\1 '"$fullVersion"'/' \
	-e 's/^(ENV PYTHON_RELEASE) .*/\1 '"${fullVersion%%[a-z]*}"'/' \
	-e 's/^(ENV PYTHON_PIP_VERSION) .*/\1 '"$pipVersion"'/' \
	-e 's/^(ENV RUST_VERSION) .*/\1 '"$rustVersion"'/' \
	-e 's!^(FROM (buildpack-deps)):.*!\1:'"${variant#*-}"'!' \
	-e 's!^(FROM (\w+)):.*!\1:'"${variant#*-}"'!'\
	"${target}"

awk -i inplace '@load "readfile"; BEGIN{l = readfile("'"${tmp}"'")}/%%WRITE_ENTRYPOINT%/{gsub("%%WRITE_ENTRYPOINT%%", l)}1' "${target}"
rm "${tmp}"
