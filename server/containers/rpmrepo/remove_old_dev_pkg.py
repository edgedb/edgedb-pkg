#!/usr/bin/env python3
from __future__ import annotations
from typing import *

import distutils.version
import os
import re

import click


# edgedb-server-1-alpha7-dev5124-1.0a7.dev5124+ged4e05af-2020101400nightly.el8.x86_64.rpm
PACKAGE_RE = re.compile(
    r"^(?P<basename>\w+(-[a-zA-Z]+)*)"
    r"(?P<slot>-\d+(-(alpha|beta|rc)\d+)?(-dev\d+)?)?"
    r"-(?P<version>[^-]*)-(?P<release>[^.]*)"
    r"(?P<ext>.*)?$",
    re.A,
)
PACKAGE_NAME_NO_DEV_RE = re.compile(r"([^-]+)((-[^-]+)*)-dev\d+")


@click.command()
@click.option("--keep", type=int, default=3)
@click.argument("path")
def main(path: str, keep: int) -> None:
    index: Dict[str, List[Tuple[str, str]]] = {}
    for file in os.scandir(path):
        m = PACKAGE_RE.match(file.name)
        if not m:
            print(file.name, "doesn't match PACKAGE_RE")
            continue

        key_with_dev = f"{m.group('basename')}{m.group('slot') or ''}"
        key = PACKAGE_NAME_NO_DEV_RE.sub(r"\1\2", key_with_dev)

        version = f"{m.group('version')}_{m.group('release')}"
        index.setdefault(key, []).append((version, file.name))

    for _, versions in index.items():
        sorted_versions = list(
            sorted(
                versions,
                key=lambda v: distutils.version.LooseVersion(v[0]),
                reverse=True,
            )
        )

        for _ver, filename in sorted_versions[keep:]:
            print("Deleting outdated", filename)
            os.unlink(os.path.join(path, filename))


if __name__ == "__main__":
    main()
