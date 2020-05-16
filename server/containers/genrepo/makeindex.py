#!/usr/bin/env python3

import argparse
import json
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
    parser.add_argument('--prefix')
    args = parser.parse_args()

    listing = sys.stdin.read()

    index = []

    for pkg in listing.split('\n'):
        if not pkg.strip():
            continue

        path = pathlib.Path(pkg)
        parts = list(path.parts)

        if len(parts) != 2:
            print('cannot parse {}'.format(pkg), file=sys.stderr)
            continue

        dist, _, arch = parts[0].rpartition('-')

        leafname = parts[1]
        m = regexp.match(str(leafname))
        if not m:
            print('cannot parse {}'.format(leafname), file=sys.stderr)
            continue

        pkgname = m.group(1)
        slot = m.group(3)
        version = m.group(6)
        revision = m.group(7)

        index.append({
            'basename': pkgname,
            'slot': slot.lstrip('-'),
            'name': '{}{}'.format(pkgname, slot),
            'version': version,
            'revision': revision,
            'architecture': arch,
            'installref': '{}{}'.format(args.prefix, pkg),
        })

    json.dump({'packages': index}, sys.stdout)


if __name__ == '__main__':
    main()
