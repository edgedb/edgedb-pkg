from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibUUID(packages.BundledCPackage):
    title = "uuid"
    name = packages.canonicalize_name("uuid")
    aliases = ["uuid-dev"]

    _server = "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/"

    sources = [
        {
            "url": _server + "v{version}/util-linux-{version}.tar.gz",
        }
    ]

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        configure = sdir / "configure"
        configure_flags = {
            "--disable-all-programs": None,
            "--enable-libuuid": None,
        }
        return self.sh_configure(build, configure, configure_flags)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["uuid"]
