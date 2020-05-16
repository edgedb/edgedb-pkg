#!/usr/bin/env python3

import argparse
import collections
import distutils.version
import pathlib
import re
import sys


regexp = re.compile(
    r"^(\w+(-[a-zA-Z]*)?)"
    r"(-\d+(-(dev|alpha|beta|rc)\d+)?)?"
    r"_([^_]*)_([^.]*)"
    r"(.*)?$",
    re.A
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subdist', type=str)
    parser.add_argument('--keep', type=int, default=5)
    args = parser.parse_args()

    listing = sys.stdin.read()

    index = collections.defaultdict(list)

    for pkg in listing.split('\n'):
        if not pkg.strip():
            continue

        path = pathlib.Path(pkg)
        leafname = path.name

        m = regexp.match(str(leafname))
        if not m:
            print('cannot parse {}'.format(leafname), file=sys.stderr)
            continue

        pkgname = m.group(1)
        slot = m.group(3)
        version = m.group(6)
        revision = m.group(7)
        revno, _, subdist = revision.rpartition('~')

        if args.subdist and subdist != args.subdist:
            continue

        index['{}{}'.format(pkgname, slot)].append(
            ('{}_{}'.format(version, revno), pkg)
        )

    for _, versions in index.items():
        sorted_versions = list(sorted(
            versions,
            key=lambda v: distutils.version.LooseVersion(v[0]),
            reverse=True,
        ))

        for ver in sorted_versions[args.keep:]:
            print(ver[1])


if __name__ == '__main__':
    main()
