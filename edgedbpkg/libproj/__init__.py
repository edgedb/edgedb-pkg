from __future__ import annotations

from metapkg import packages
from metapkg import targets

from edgedbpkg import libsqlite3, libtiff


class LibProj(packages.BundledCMakePackage):
    title = "libproj"
    ident = "libproj"
    aliases = ["libproj-dev"]

    _server = "https://github.com/OSGeo/PROJ/releases/download/"
    _data_server = "https://github.com/OSGeo/PROJ-data/releases/download/"

    sources = [
        {
            "url": _server + "{version}/proj-{version}.tar.gz",
        },
        # {
        #     "url": _data_server + "1.19.0/proj-data-1.19.tar.gz",
        #     "path": "data/",
        #     "extras": {
        #         "strip_components": 0,
        #     },
        # },
    ]

    artifact_requirements = [
        "libsqlite3 (>=3.31)",
        "libtiff (>=4.0)",
    ]

    artifact_build_requirements = [
        "libsqlite3-dev (>=3.31)",
        "libtiff-dev (>=4.0)",
    ]

    bundle_deps = [
        libsqlite3.LibSQLite3("3.46.1"),
        libtiff.LibTIFF("4.7.0"),
    ]

    def get_dep_pkg_name(self) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "PROJ"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        conf_args = super().get_configure_args(build, wd=wd) | {
            "-DBUILD_TESTING": "OFF",
            "-DBUILD_PROJSYNC": "OFF",
            "-DENABLE_CURL": "OFF",
            "-DENABLE_TIFF": "ON",
            "-DBUILD_APPS": "OFF",
            "-DEMBED_PROJ_DATA_PATH": "OFF",
        }

        sqlite_pkg = build.get_package("libsqlite3")
        if build.is_bundled(sqlite_pkg):
            sqlite_bin_path = build.sh_get_bundled_pkg_bin_path(
                sqlite_pkg, relative_to="pkgbuild"
            )
            conf_args["-DEXE_SQLITE3"] = f"!{sqlite_bin_path}/sqlite3"

        return conf_args

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["proj"]
