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
    re.A,
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
    re.X | re.A,
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
        raise ValueError(f"cannot parse version: {ver}")
    metadata = []
    prerelease: List[str] = []
    if v.group("pre"):
        pre_l = v.group("pre_l")
        if pre_l in {"a", "alpha"}:
            pre_kind = "alpha"
        elif pre_l in {"b", "beta"}:
            pre_kind = "beta"
        elif pre_l in {"c", "rc"}:
            pre_kind = "rc"
        else:
            raise ValueError(f"cannot determine release stage from {ver}")

        prerelease.append(f"{pre_kind}.{v.group('pre_n')}")
        if v.group("dev"):
            prerelease.append(f'dev.{v.group("dev_n")}')

    elif v.group("dev"):
        prerelease.append("alpha.1")
        prerelease.append(f'dev.{v.group("dev_n")}')

    if v.group("local"):
        metadata.extend(v.group("local").split("."))

    release = [int(r) for r in v.group("release").split(".")]

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
        ver_key += "~" + "".join(prerelease).lstrip(".~")
    if revision:
        ver_key += f".{revision}"
    return ver_key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repopath")
    parser.add_argument("outputdir")
    parser.add_argument("repoids")
    args = parser.parse_args()

    for dist in args.repoids.split(","):
        result = subprocess.run(
            [
                "repoquery",
                "--repofrompath={rid},{path}".format(
                    rid=dist,
                    path=os.path.join(args.repopath, dist),
                ),
                "--repoid={}".format(dist),
                "--qf=%{name}|%{version}|%{release}|%{arch}",
                "-q",
                "*",
            ],
            universal_newlines=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        index = []

        for line in result.stdout.split("\n"):
            if not line.strip():
                continue

            pkgname, pkgver, release, arch = line.split("|")

            m = slot_regexp.match(pkgname)
            if not m:
                print("cannot parse package name: {}".format(pkgname))
                basename = pkgname
                slot = None
            else:
                basename = m.group(1)
                slot = m.group(2)

            parsed_ver = parse_version(pkgver)

            installref = "{}-{}-{}.{}".format(pkgname, pkgver, release, arch)
            index.append(
                {
                    "basename": basename,
                    "slot": slot,
                    "name": pkgname,
                    "version": pkgver,
                    "parsed_version": parsed_ver,
                    "version_key": format_version_key(parsed_ver, release),
                    "revision": release,
                    "architecture": arch,
                    "installref": installref,
                }
            )

            print("makeindex: noted {}".format(installref))

        out = os.path.join(args.outputdir, "{}.json".format(dist))
        with open(out, "w") as f:
            json.dump({"packages": index}, f)


if __name__ == "__main__":
    main()
