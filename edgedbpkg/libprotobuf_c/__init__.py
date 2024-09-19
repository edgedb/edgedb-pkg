from __future__ import annotations

from metapkg import packages
from metapkg import targets

# from edgedbpkg import protobuf


class LibProtoBufC(packages.BundledCAutoconfPackage):
    title = "libprotobuf-c"
    name = packages.canonicalize_name("libprotobuf-c")
    aliases = ["libprotobuf-c-dev"]

    _server = "https://github.com/protobuf-c/protobuf-c/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/protobuf-c-{version}.tar.gz",
        },
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--disable-protoc": None,
        }

    def get_make_args(
        self,
        build: targets.Build,
    ) -> packages.Args:
        return super().get_make_args(build) | {
            "V": "100",
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["protobuf-c"]
