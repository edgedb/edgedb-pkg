from __future__ import annotations

from metapkg import packages
from metapkg import targets

from edgedbpkg import libproj, libtiff, zlib


class LibGeoTIFF(packages.BundledCAutoconfPackage):
    title = "libgeotiff"
    ident = "libgeotiff"
    aliases = ["libgeotiff-dev"]

    _server = "https://download.osgeo.org/geotiff/"

    sources = [
        {
            "url": _server + "libgeotiff/libgeotiff-{version}.tar.gz",
        },
    ]

    artifact_requirements = [
        "libproj (>=6.1.0)",
        "libtiff (>=3.9.1)",
        "zlib",
    ]

    artifact_build_requirements = [
        "libproj-dev (>=6.1.0)",
        "libtiff-dev (>=3.9.1)",
        "zlib-dev",
    ]

    bundle_deps = [
        libproj.LibProj("9.5.0"),
        libtiff.LibTIFF("4.7.0"),
        zlib.Zlib("1.3.1"),
    ]

    def get_dep_pkg_name(self) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "GEOTIFF"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        conf_args = super().get_configure_args(build, wd=wd) | {
            "--without-jpeg": None,
        }

        deps = {
            "libproj": "proj",
            "libtiff": "libtiff",
            "zlib": "zlib",
        }

        for dep, key in deps.items():
            dep_pkg = build.get_package(dep)
            if build.is_bundled(dep_pkg):
                path = build.sh_get_bundled_install_path(dep_pkg, wd=wd)
                conf_args[f"--with-{key}"] = f"!{path}"
            else:
                conf_args[f"--with-{key}"] = ""

        return conf_args

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["geotiff"]
