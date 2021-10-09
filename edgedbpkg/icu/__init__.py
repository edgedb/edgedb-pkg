from __future__ import annotations

import pathlib
import textwrap

from metapkg import packages
from metapkg import targets


class ICU(packages.BundledPackage):

    title = "ICU"
    name = "icu"
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

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        configure = sdir / "source" / "configure"

        configure_flags = {
            "--prefix": str(build.get_full_install_prefix()),
            "--disable-samples": None,
            "--disable-tests": None,
            "--enable-rpath": None,
        }

        return build.sh_format_command(configure, configure_flags)

    def get_build_script(self, build: targets.Build) -> str:
        make = build.sh_get_command("make")

        return textwrap.dedent(
            f"""\
            {make}
        """
        )

    def get_build_install_script(self, build: targets.Build) -> str:
        installdest = build.get_install_dir(self, relative_to="pkgbuild")
        make = build.sh_get_command("make")

        return textwrap.dedent(
            f"""\
            {make} DESTDIR=$(pwd)/"{installdest}" install
        """
        )

    def get_shlib_paths(self, build: targets.Build) -> list[pathlib.Path]:
        return [build.get_full_install_prefix() / "lib"]

    def get_include_paths(self, build: targets.Build) -> list[pathlib.Path]:
        return [build.get_full_install_prefix() / "include"]
