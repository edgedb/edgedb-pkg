from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibPCRE2(packages.BundledCAutoconfPackage):
    title = "libpcre2"
    name = packages.canonicalize_name("libpcre2")
    aliases = ["libpcre2-dev"]

    _server = "https://github.com/PCRE2Project/pcre2/releases/download/"

    sources = [
        {
            "url": _server + "pcre2-{version}/pcre2-{version}.tar.bz2",
        }
    ]

    @classmethod
    def get_dep_pkg_name(cls) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "PCRE2"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--enable-pcre2-8": None,
            "--disable-pcre2-16": None,
            "--disable-pcre2-32": None,
            "--enable-shared": None,
            "--enable-jit": None,
            "--enable-unicode": None,
            "--disable-static": None,
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return [
            "pcre2-8",
        ]
