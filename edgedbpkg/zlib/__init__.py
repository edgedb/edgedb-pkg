from __future__ import annotations

from metapkg import packages
from metapkg import targets


class Zlib(packages.BundledCMakePackage):
    title = "zlib"
    ident = "zlib"
    aliases = ["zlib-dev"]

    _server = "https://zlib.net/fossils/"

    sources = [
        {
            "url": _server + "zlib-{version}.tar.gz",
        }
    ]

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["z"]
