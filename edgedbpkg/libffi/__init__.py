from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibFFI(packages.BundledCPackage):
    title = "libffi"
    name = "libffi"
    aliases = ["libffi-dev"]

    _server = "https://github.com/libffi/libffi/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/libffi-{version}.tar.gz",
        }
    ]

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        configure = sdir / "configure"
        configure_flags = {
            "--disable-multi-os-directory": None,
        }

        return self.sh_configure(build, configure, configure_flags)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["ffi"]
