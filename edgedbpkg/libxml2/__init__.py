from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibXML2(packages.BundledCAutoconfPackage):
    title = "libxml2"
    name = packages.canonicalize_name("libxml2")
    aliases = ["libxml2-dev"]

    _server = "https://download.gnome.org/sources/libxml2/"

    sources = [
        {
            "url": _server + "{major_minor_v}/libxml2-{version}.tar.xz",
        },
    ]

    def get_dep_pkg_config_script(self) -> str | None:
        return "xml2-config"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--without-icu": None,
            "--without-lzma": None,
            "--disable-static": None,
            "--without-readline": None,
            "--without-history": None,
            "--without-python": None,
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["xml2"]
