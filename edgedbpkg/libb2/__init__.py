from __future__ import annotations

import pathlib

from metapkg import packages
from metapkg import targets


class LibB2(packages.BundledCPackage):
    title = "libb2"
    name = packages.canonicalize_name("libb2")
    aliases = ["libb2-dev"]

    _server = "https://github.com/BLAKE2/libb2/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/libb2-{version}.tar.gz",
        }
    ]

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        # Restore modification times to avoid invoking the autotools.
        script = (
            f'touch -r "{sdir}/aclocal.m4" "{sdir}/configure.ac"'
            f' "{sdir}/configure"\n'
        )
        configure = sdir / "configure"
        configure_flags: dict[str, str | pathlib.Path | None] = {
            "--disable-openmp": None,
            "--disable-native": None,
        }
        if build.target.machine_architecture == "x86_64":
            configure_flags["--enable-fat"] = None
        else:
            configure_flags["--disable-fat"] = None

        # Upstream defaults to -O3, so likely should we.
        build.sh_append_flags(
            configure_flags,
            "CFLAGS",
            ("-O3",),
        )

        return script + self.sh_configure(build, configure, configure_flags)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["b2"]

    def get_private_libraries(self, build: targets.Build) -> list[str]:
        return ["libb2.*"]
