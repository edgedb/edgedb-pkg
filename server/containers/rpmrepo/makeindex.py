#!/usr/bin/env python3.8
from __future__ import annotations
from typing import *
from typing_extensions import TypedDict

import argparse
import json
import os.path
import re
import subprocess


slot_regexp = re.compile(
    r"^(\w+(?:-[a-zA-Z]*)*?)"
    r"(?:-(\d+(?:-(?:alpha|beta|rc)\d+)?(?:-dev\d+)?))?$",
    re.A
)


version_regexp = re.compile(
    r"""^
    (?P<release>[0-9]+(?:\.[0-9]+)*)
    (?P<pre>
        [-_]?
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
    stage: str
    stage_no: int
    local: Tuple[str, ...]


def parse_version(ver: str) -> Version:
    v = version_regexp.match(ver)
    if v is None:
        raise ValueError(f'cannot parse version: {ver}')
    local = []
    if v.group('pre'):
        pre_l = v.group('pre_l')
        if pre_l in {'a', 'alpha'}:
            stage = 'alpha'
        elif pre_l in {'b', 'beta'}:
            stage = 'beta'
        elif pre_l in {'c', 'rc'}:
            stage = 'rc'
        else:
            raise ValueError(f'cannot determine release stage from {ver}')

        stage_no = int(v.group('pre_n'))
        if v.group('dev'):
            local.extend([f'dev{v.group("dev_n")}'])
    elif v.group('dev'):
        stage = 'dev'
        stage_no = int(v.group('dev_n'))
    else:
        stage = 'final'
        stage_no = 0

    if v.group('local'):
        local.extend(v.group('local').split('.'))

    release = [int(r) for r in v.group('release').split('.')]

    return Version(
        major=release[0],
        minor=release[1],
        patch=release[2] if len(release) == 3 else 0,
        stage=stage,
        stage_no=stage_no,
        local=tuple(local),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repopath')
    parser.add_argument('outputdir')
    parser.add_argument('repoids')
    args = parser.parse_args()

    for dist in args.repoids.split(','):
        result = subprocess.run(
            [
                'repoquery',
                '--repofrompath={rid},{path}'.format(
                    rid=dist,
                    path=os.path.join(args.repopath, dist),
                ),
                '--repoid={}'.format(dist),
                '--qf=%{name}|%{version}|%{release}|%{arch}',
                '-q',
                '*',
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

            pkgname, pkgver, release, arch = line.split('|')

            m = slot_regexp.match(pkgname)
            if not m:
                print('cannot parse package name: {}'.format(pkgname))
                basename = pkgname
                slot = None
            else:
                basename = m.group(1)
                slot = m.group(2)

            installref = '{}-{}-{}.{}'.format(pkgname, pkgver, release, arch)
            index.append({
                'basename': basename,
                'slot': slot,
                'name': pkgname,
                'version': pkgver,
                'parsed_version': parse_version(pkgver),
                'revision': release,
                'architecture': arch,
                'installref': installref
            })

            print('makeindex: noted {}'.format(installref))

        out = os.path.join(args.outputdir, '{}.json'.format(dist))
        with open(out, 'w') as f:
            json.dump({'packages': index}, f)


if __name__ == '__main__':
    main()
