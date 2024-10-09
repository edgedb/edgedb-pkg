from __future__ import annotations

from metapkg import packages

from edgedbpkg import protobuf


class ProtoCompilerC(packages.BundledCAutoconfPackage):
    title = "protoc-c"
    name = packages.canonicalize_name("protoc-c")

    _server = "https://github.com/protobuf-c/protobuf-c/releases/download/"

    sources = [
        {
            "url": _server + "v{version}/protobuf-c-{version}.tar.gz",
        },
    ]

    artifact_requirements = [
        "protobuf (>=3)",
    ]

    artifact_build_requirements = [
        "protobuf (>=3)",
    ]

    bundle_deps = [
        protobuf.ProtoBuf("28.2"),
    ]

    @property
    def provides_build_tools(cls) -> bool:
        return True
