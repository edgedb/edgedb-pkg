#!/usr/bin/env python3
from __future__ import annotations
from typing import *
from typing_extensions import TypedDict

import argparse
import fnmatch
import json
import pathlib
import re
import subprocess
import tarfile
import tempfile


slot_regexp = re.compile(
    r"^(\w+(?:-[a-zA-Z]*)*?)"
    r"(?:-(\d+(?:-(?:alpha|beta|rc)\d+)?(?:-dev\d+)?))?$",
    re.A
)


version_regexp = re.compile(
    r"""^
    (?P<release>[0-9]+(?:\.[0-9]+)*)
    (?P<pre>
        [-]?
        (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
        [\.]?
        (?P<pre_n>[0-9]+)?
    )?
    (?P<dev>
        [\.]?
        (?P<dev_l>dev)
        [\.]?
        (?P<dev_n>[0-9]+)?
    )?
    (?:\+(?P<local>[a-z0-9]+(?:[\.][a-z0-9]+)*))?
    $""",
    re.X | re.A
)


class Version(TypedDict):

    major: int
    minor: int
    patch: int
    prerelease: Tuple[str, ...]
    metadata: Tuple[str, ...]


def parse_version(ver: str) -> Version:
    v = version_regexp.match(ver)
    if v is None:
        raise ValueError(f'cannot parse version: {ver}')
    metadata = []
    prerelease: List[str] = []
    if v.group('pre'):
        pre_l = v.group('pre_l')
        if pre_l in {'a', 'alpha'}:
            pre_kind = 'alpha'
        elif pre_l in {'b', 'beta'}:
            pre_kind = 'beta'
        elif pre_l in {'c', 'rc'}:
            pre_kind = 'rc'
        else:
            raise ValueError(f'cannot determine release stage from {ver}')

        prerelease.append(f"{pre_kind}.{v.group('pre_n')}")
        if v.group('dev'):
            prerelease.append(f'dev.{v.group("dev_n")}')

    elif v.group('dev'):
        prerelease.append('alpha.1')
        prerelease.append(f'dev.{v.group("dev_n")}')

    if v.group('local'):
        metadata.extend(v.group('local').split('.'))

    release = [int(r) for r in v.group('release').split('.')]

    return Version(
        major=release[0],
        minor=release[1],
        patch=release[2] if len(release) == 3 else 0,
        prerelease=tuple(prerelease),
        metadata=tuple(metadata),
    )


def format_version_key(ver: Version, revision: str) -> str:
    ver_key = f'{ver["major"]}.{ver["minor"]}.{ver["patch"]}'
    if ver["prerelease"]:
        # Using tilde for "dev" makes it sort _before_ the equivalent
        # version without "dev" when using the GNU version sort (sort -V)
        # or debian version comparison algorithm.
        prerelease = (
            ("~" if pre.startswith("dev.") else ".") + pre
            for pre in ver["prerelease"]
        )
        ver_key += '~' + ''.join(prerelease).lstrip('.~')
    if revision:
        ver_key += f".{revision}"
    return ver_key


def extract_catver(path: str) -> Optional[int]:
    cv_prefix = 'EDGEDB_CATALOG_VERSION = '
    defines_pattern = (
        '*/usr/lib/*-linux-gnu/edgedb-server-*/lib/python*/site-packages/edb'
        + '/server/defines.py'
    )

    with tempfile.TemporaryDirectory() as _td:
        td = pathlib.Path(_td)
        subprocess.run(['ar', 'x', path, 'data.tar.xz'], cwd=_td)
        with tarfile.open(td / 'data.tar.xz', 'r:xz') as tarf:
            for member in tarf.getmembers():
                if fnmatch.fnmatch(member.path, defines_pattern):
                    df = tarf.extractfile(member)
                    if df is not None:
                        for lb in df.readlines():
                            line = lb.decode()
                            if line.startswith(cv_prefix):
                                return int(line[len(cv_prefix):])

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full-regen', action='store_true')
    parser.add_argument('repopath')
    parser.add_argument('outputdir')
    args = parser.parse_args()

    result = subprocess.run(
        ['reprepro', '-b', args.repopath, 'dumpreferences'],
        universal_newlines=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    dists = set()

    for line in result.stdout.split('\n'):
        if not line.strip():
            continue

        dist, _, _ = line.partition('|')
        dists.add(dist)

    list_format = r'\0'.join((
        r'${$architecture}',
        r'${package}',
        r'${version}',
        r'${$fullfilename}',
    )) + r'\n'

    idxdir = pathlib.Path(args.outputdir)

    for dist in dists:
        idxfile = idxdir / f'{dist}.json'
        existing = {}

        if idxfile.exists():
            with open(idxfile, 'r') as f:
                index = json.load(f)
                if index and 'packages' in index:
                    for entry in index['packages']:
                        if 'version_key' in entry:
                            existing[
                                entry['name'], entry['version_key']
                            ] = entry

        result = subprocess.run(
            [
                'reprepro', '-b', args.repopath,
                f'--list-format={list_format}',
                'list', dist,
            ],
            universal_newlines=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        index = []
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue

            arch, pkgname, pkgver, pkgfile = line.split('\0')
            relver, _, revver = pkgver.rpartition('-')

            m = slot_regexp.match(pkgname)
            if not m:
                print('cannot parse package name: {}'.format(pkgname))
                basename = pkgname
                slot = None
            else:
                basename = m.group(1)
                slot = m.group(2)

            if arch == 'amd64':
                arch = 'x86_64'

            parsed_ver = parse_version(relver)
            version_key = format_version_key(parsed_ver, revver)

            if (pkgname, version_key) in existing and not args.full_regen:
                index.append(existing[pkgname, version_key])
                continue

            if (
                not any(m.startswith('cv') for m in parsed_ver["metadata"])
                and basename == 'edgedb-server'
            ):
                if not pathlib.Path(pkgfile).exists():
                    print(f'package file does not exist: {pkgfile}')
                else:
                    catver = extract_catver(pkgfile)
                    if catver is None:
                        print(f'cannot extract catalog version from {pkgfile}')
                    else:
                        parsed_ver["metadata"] += (f"cv{catver}",)
                        print(f'extracted catver {catver} from {pkgfile}')

            installref = '{}={}-{}'.format(pkgname, relver, revver)

            index.append({
                'basename': basename,
                'slot': slot,
                'name': pkgname,
                'version': relver,
                'parsed_version': parsed_ver,
                'version_key': version_key,
                'revision': revver,
                'architecture': arch,
                'installref': installref,
            })

            print('makeindex: noted {}'.format(installref))

        with open(idxfile, 'w') as f:
            json.dump({'packages': index}, f)


if __name__ == '__main__':
    main()
