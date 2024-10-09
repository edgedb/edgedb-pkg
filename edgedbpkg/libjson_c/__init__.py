from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibJsonC(packages.BundledCMakePackage):
    title = "libjson-c"
    name = packages.canonicalize_name("libjson-c")
    aliases = ["libjson-c-dev"]

    _server = "https://s3.amazonaws.com/json-c_releases/releases/"

    sources = [
        {
            "url": _server + "json-c-{version}.tar.gz",
        },
    ]

    @classmethod
    def get_dep_pkg_name(cls) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "JSONC"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "-DBUILD_APPS": "OFF",
            "-DBUILD_STATIC_LIBS": "OFF",
            "-DDISABLE_EXTRA_LIBS": "ON",
            "-DDISABLE_WERROR": "ON",
            "-DENABLE_RDRAND": "OFF",
            "-DENABLE_THREADING": "ON",
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["json-c"]
