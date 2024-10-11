from __future__ import annotations

from metapkg import packages
from metapkg import targets

from edgedbpkg import libabseil
from edgedbpkg import libjsoncpp
from edgedbpkg import zlib


class ProtoBuf(packages.BundledCMakePackage):
    title = "protobuf"
    name = packages.canonicalize_name("protobuf")

    _server = "https://github.com/protocolbuffers/protobuf/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/protobuf-{version}.tar.gz",
        },
    ]

    artifact_requirements = [
        "libabsl (>=20230802.0)",
        "libjsoncpp (>=1.7.4)",
        "zlib",
    ]

    artifact_build_requirements = [
        "libabsl-dev (>=20230802.0)",
        "libjsoncpp-dev (>=1.7.4)",
        "zlib-dev",
    ]

    bundle_deps = [
        libabseil.LibAbseil("20240722.0"),
        libjsoncpp.LibJsonCpp("1.9.6"),
        zlib.Zlib("1.3.1"),
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        return super().get_configure_args(build, wd=wd) | {
            "-Dprotobuf_BUILD_CONFORMANCE": "no",
            "-Dprotobuf_BUILD_EXAMPLES": "no",
            "-Dprotobuf_BUILD_LIBPROTOC": "yes",
            "-Dprotobuf_BUILD_LIBUPB": "no",
            "-Dprotobuf_BUILD_PROTOBUF_BINARIES": "yes",
            "-Dprotobuf_BUILD_PROTOC_BINARIES": "yes",
            "-Dprotobuf_BUILD_SHARED_LIBS": "yes",
            "-Dprotobuf_BUILD_TESTS": "no",
            "-Dprotobuf_DISABLE_RTTI": "no",
            "-Dprotobuf_INSTALL": "yes",
            "-Dprotobuf_INSTALL_EXAMPLES": "no",
            "-Dprotobuf_TEST_XML_OUTDIR": "no",
            "-Dprotobuf_WITH_ZLIB": "yes",
            "-Dprotobuf_VERBOSE": "no",
            "-DCMAKE_MODULE_PATH": f"{sdir}/cmake",
            "-Dprotobuf_ABSL_PROVIDER": "package",
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return [
            "protobuf",
            "protoc",
        ]
