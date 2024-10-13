from __future__ import annotations

import shlex

from metapkg import packages
from metapkg import targets


class ICU(packages.BundledCAutoconfPackage):
    title = "ICU"
    ident = "icu"
    aliases = ["icu-dev"]

    _server = "https://github.com/unicode-org/icu/releases/download/"

    sources = [
        {
            "url": (
                _server
                + "release-{dash_version}/"
                + "icu4c-{underscore_version}-src.tgz"
            ),
        }
    ]

    def sh_get_configure_command(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        return shlex.quote(str(sdir / "source" / "configure"))

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd) | {
            "--disable-samples": None,
            "--disable-tests": None,
            "--enable-rpath": None,
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["icui18n", "icuuc", "icudata"]
