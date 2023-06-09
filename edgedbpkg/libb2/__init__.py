from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibB2(packages.BundledCPackage):

    title = "libb2"
    name = "libb2"
    aliases = ["libb2-dev"]

    _server = "https://github.com/BLAKE2/libb2/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/libb2-{version}.tar.gz",
        }
    ]

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["b2"]
