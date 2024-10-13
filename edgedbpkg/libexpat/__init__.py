from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibExpat(packages.BundledCAutoconfPackage):
    title = "libexpat"
    ident = "libexpat"
    aliases = ["libexpat-dev"]

    _server = "https://github.com/libexpat/libexpat/releases/download/"

    sources = [
        {
            "url": _server + "R_{underscore_version}/expat-{version}.tar.xz",
        }
    ]

    @classmethod
    def get_dep_pkg_name(cls) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "EXPAT"

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["expat"]
