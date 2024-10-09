from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibJsonCpp(packages.BundledCMesonPackage):
    title = "libjsoncpp"
    name = packages.canonicalize_name("libjsoncpp")
    aliases = ["libjsoncpp-dev"]

    _server = "https://github.com/open-source-parsers/jsoncpp/archive/"

    sources = [
        {
            "url": _server + "{version}.tar.gz",
        },
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--includedir": (
                build.get_install_path(self, "include") / "jsoncpp"
            ),
            "-Dtests": "false",
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["jsoncpp"]
