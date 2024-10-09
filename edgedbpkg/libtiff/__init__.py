from __future__ import annotations

from metapkg import packages
from metapkg import targets

from edgedbpkg import zlib


class LibTIFF(packages.BundledCAutoconfPackage):
    title = "libtiff"
    name = packages.canonicalize_name("libtiff")
    aliases = ["libtiff-dev"]

    _server = "https://download.osgeo.org/libtiff/"

    sources = [
        {
            "url": _server + "tiff-{version}.tar.xz",
        },
    ]

    artifact_requirements = [
        "zlib",
    ]

    artifact_build_requirements = [
        "zlib-dev",
    ]

    bundle_deps = [
        zlib.Zlib("1.3.1"),
    ]

    @classmethod
    def get_dep_pkg_name(cls) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "TIFF"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--disable-sphinx": None,
            "--disable-cxx": None,
            "--disable-jbig": None,
            "--disable-jpeg": None,
            "--disable-opengl": None,
            "--disable-lzma": None,
            "--disable-static": None,
            "--disable-tests": None,
            "--disable-webp": None,
            "--enable-zlib": None,
            "--disable-zstd": None,
            "--disable-libdeflate": None,
            "--disable-docs": None,
            "--disable-contrib": None,
            "--disable-tools": None,
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["tiff"]
