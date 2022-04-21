from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibPCRE2(packages.BundledCPackage):

    title = "libpcre2"
    name = "libpcre2"
    aliases = ["libpcre2-dev"]

    _server = "https://github.com/PCRE2Project/pcre2/releases/download/"

    sources = [
        {
            "url": _server + "pcre2-{version}/pcre2-{version}.tar.bz2",
        }
    ]

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        configure = sdir / "configure"
        configure_flags = {
            "--enable-pcre2-8": None,
            "--enable-jit": None,
            "--enable-pcre2grep-jit": None,
            "--enable-pcre2-16": None,
            "--enable-pcre2-32": None,
            "--enable-unicode": None,
        }

        if self.options.get("static", False):
            configure_flags["--enable-static"] = None
        else:
            configure_flags["--disable-static"] = None

        if self.options.get("shared", True):
            configure_flags["--enable-shared"] = None
        else:
            configure_flags["--disable-shared"] = None

        return self.sh_configure(build, configure, configure_flags)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["pcre2"]
