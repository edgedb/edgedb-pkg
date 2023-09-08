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

if which xcode-select >/dev/null 2>&1; then
	# macOS
	SED="$(which gsed)"
	JQ="$(which jq)"
	READLINK="$(which greadlink)"
	AWK="$(which gawk)"
	if [[ ! -e $SED ]]; then
		echo "Install gnu-sed with 'brew install gnu-sed'"
		exit 1
	fi
	if [[ ! -e $JQ ]]; then
		echo "Install jq with 'brew install jq'"
		exit 1
	fi
	if [[ ! -e $READLINK ]]; then
		echo "Install gnu-readlink with 'brew install coreutils'"
		exit 1
	fi
	if [[ ! -e $AWK ]]; then
		echo "Install gnu-awk with 'brew install gawk'"
		exit 1
	fi
else
	SED="$(which sed)"
	JQ="$(which jq)"
	READLINK="$(which readlink)"
	AWK="$(which awk)"
fi


cd "$(dirname "$($READLINK -f "$BASH_SOURCE")")"

version="3.9"
pipVersion="$(curl -fsSL 'https://pypi.org/pypi/pip/json' | $JQ -r .info.version)"
rustVersion="1.71.1"
# Do not bump NodeJS to newer, binary releases incompatible with older glibc
nodeVersion="16.16.0"
yarnVersion="1.22.19"
goVersion="1.21"

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
				| $SED -r -e 's/\\/\\\\/g' \
				| $SED -r -e 's/\x27/\x27\\\x27\x27/g' \
				| $SED -r -e 's/^(.*)$/\1\\n\\/g' \
				| $SED -r -e 's/&/\\&/g')"
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
			| $SED -r 's!^.*refs/tags/v([0-9a-z.]+).*$!\1!' \
			| grep $rcGrepV -E -- '[a-zA-Z]+' \
			|| :

		# this page has a very aggressive varnish cache in front of it, which is why we also scrape tags from GitHub
		curl -fsSL 'https://www.python.org/ftp/python/' \
			| grep '<a href="'"$rcVersion." \
			| $SED -r 's!.*<a href="([^"/]+)/?".*!\1!' \
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
			| $SED -r 's!.*<a href="Python-([^"/]+)\.tar\.xz".*!\1!' \
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

$SED -ri \
	-e 's/^(ENV PYTHON_VERSION) .*/\1 '"$fullVersion"'/' \
	-e 's/^(ENV PYTHON_RELEASE) .*/\1 '"${fullVersion%%[a-z]*}"'/' \
	-e 's/^(ENV PYTHON_PIP_VERSION) .*/\1 '"$pipVersion"'/' \
	-e 's/^(ENV RUST_VERSION) .*/\1 '"$rustVersion"'/' \
	-e 's/^(ENV NODE_VERSION) .*/\1 '"$nodeVersion"'/' \
	-e 's/^(ENV YARN_VERSION) .*/\1 '"$yarnVersion"'/' \
	-e 's/^(ENV GO_VERSION) .*/\1 '"$goVersion"'/' \
	-e 's!^(FROM (buildpack-deps)):%%PLACEHOLDER%%!\1:'"${variant#*-}"'!' \
	-e 's!^(FROM (\w+)):%%PLACEHOLDER%%!\1:'"${variant#*-}"'!'\
	"${target}"

# Add GPG keys
new_line=' \\\
'
for key_file in _keys/*.keys; do
	key_file_basename=$(basename "${key_file}")
	key_type=${key_file_basename%.*}
	while read -r line; do
		pattern='"\$\{'$(echo "${key_type}" | tr '[:lower:]' '[:upper:]')'_KEYS\[@\]\}"'
		sed -Ei -e "s/([ \\t]*)(${pattern})/\\1${line}${new_line}\\1\\2/" "${target}"
	done < "_keys/${key_type}.keys"
	sed -Ei -e "/${pattern}/d" "${target}"
done

$AWK -i inplace '@load "readfile"; BEGIN{l = readfile("'"${tmp}"'")}/%%WRITE_ENTRYPOINT%/{gsub("%%WRITE_ENTRYPOINT%%", l)}1' "${target}"
rm "${tmp}"
