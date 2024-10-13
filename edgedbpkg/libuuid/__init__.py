from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibUUID(packages.BundledCAutoconfPackage):
    title = "uuid"
    ident = "uuid"
    aliases = ["uuid-dev"]

    _server = "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/"

    sources = [
        {
            "url": _server + "v{major_minor_v}/util-linux-{version}.tar.gz",
        }
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--disable-all-programs": None,
            "--enable-libuuid": None,
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["uuid"]
