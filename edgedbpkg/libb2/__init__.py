from __future__ import annotations

import pathlib

from metapkg import packages
from metapkg import targets


class LibB2(packages.BundledCAutoconfPackage):
    title = "libb2"
    name = packages.canonicalize_name("libb2")
    aliases = ["libb2-dev"]

    _server = "https://github.com/BLAKE2/libb2/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/libb2-{version}.tar.gz",
        }
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        args = dict(super().get_configure_args(build, wd=wd)) | {
            "--disable-openmp": None,
            "--disable-native": None,
        }

        if build.target.machine_architecture == "x86_64":
            args["--enable-fat"] = None
        else:
            args["--disable-fat"] = None

        # Upstream defaults to -O3, so likely should we.
        build.sh_append_flags(
            args,
            "CFLAGS",
            ("-O3",),
        )

        return args

    def get_configure_script(self, build: targets.Build) -> str:
        # Restore modification times to avoid invoking the autotools.
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        touch = f'touch -r "{sdir}/aclocal.m4" "{sdir}/configure.ac"\n'
        return touch + super().get_configure_script(build)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["b2"]

    def get_private_libraries(self, build: targets.Build) -> list[str]:
        return ["libb2.*"]
