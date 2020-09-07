#!/usr/bin/env python3

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


def main():
    parser = argparse.ArgumentParser()
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

    for dist in dists:
        result = subprocess.run(
            ['reprepro', '-b', args.repopath, 'list', dist],
            universal_newlines=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        index = []
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue

            dist_info, _, pkg = line.partition(':')
            if not dist_info or not pkg:
                continue

            distname, component, arch = dist_info.strip().split('|')
            pkgname, pkgver = pkg.strip().split()
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

            index.append({
                'basename': basename,
                'slot': slot,
                'name': pkgname,
                'version': relver,
                'revision': revver,
                'architecture': arch,
                'installref': '{}={}-{}'.format(pkgname, relver, revver),
            })

        out = os.path.join(args.outputdir, '{}.json'.format(dist))
        with open(out, 'w') as f:
            json.dump({'packages': index}, f)


if __name__ == '__main__':
    main()
