from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibGEOS(packages.BundledCMakePackage):
    title = "libgeos"
    ident = "libgeos"
    aliases = ["libgeos-dev"]

    _server = "https://github.com/libgeos/geos/releases/download/"

    sources = [
        {
            "url": _server + "{version}/geos-{version}.tar.bz2",
        },
    ]

    def get_dep_pkg_name(self) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "GEOS"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        conf_args = super().get_configure_args(build, wd=wd) | {
            "-DBUILD_TESTING": "OFF",
            "-DBUILD_DOCUMENTATION": "OFF",
        }

        arch = build.target.machine_architecture
        if arch == "arm64":
            conf_args["-DDISABLE_GEOS_INLINE"] = "ON"

        return conf_args

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return [
            "geos",
            "geos_c",
        ]
