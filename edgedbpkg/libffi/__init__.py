from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibFFI(packages.BundledCAutoconfPackage):
    title = "libffi"
    ident = "libffi"
    aliases = ["libffi-dev"]

    _server = "https://github.com/libffi/libffi/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/libffi-{version}.tar.gz",
        }
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--disable-multi-os-directory": None,
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["ffi"]
