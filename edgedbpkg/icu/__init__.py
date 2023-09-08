from __future__ import annotations

from metapkg import packages
from metapkg import targets


class ICU(packages.BundledCPackage):
    title = "ICU"
    name = packages.canonicalize_name("icu")
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
            "--disable-samples": None,
            "--disable-tests": None,
            "--enable-rpath": None,
        }
        return self.sh_configure(build, configure, configure_flags)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["icui18n", "icuuc", "icudata"]
