#!/usr/bin/env python3.8

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

            index.append({
                'basename': basename,
                'slot': slot,
                'name': pkgname,
                'version': pkgver,
                'revision': release,
                'architecture': arch,
                'installref': '{}-{}-{}.{}'.format(
                    pkgname, pkgver, release, arch
                )
            })

        out = os.path.join(args.outputdir, '{}.json'.format(dist))
        with open(out, 'w') as f:
            json.dump({'packages': index}, f)


if __name__ == '__main__':
    main()
