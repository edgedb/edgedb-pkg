from __future__ import annotations
from typing import (
    Any,
)

from metapkg import packages
from metapkg import targets


class EdgeDBCLI(packages.BundledRustPackage):

    title = "EdgeDBCLI"
    name = "edgedb-cli"
    description = "EdgeDB Command Line Tools"
    license_id = "Apache-2.0"
    group = "Applications/Databases"
    identifier = "com.edgedb.edgedb-cli"
    url = "https://edgedb.com/"

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb-cli.git",
        },
    ]

    def get_package_layout(
        self, build: targets.Build
    ) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.FLAT

    def get_license_files_pattern(self) -> str:
        return ""

    def get_artifact_metadata(self, build: targets.Build) -> dict[str, Any]:
        metadata = dict(super().get_artifact_metadata(build))
        metadata["publish_link_to_latest"] = True
        return metadata

    def get_build_script(self, build: targets.Build) -> str:
        if build.channel == "stable" and not self.version.is_stable():
            raise AssertionError(
                f"cannot build non-stable edgedb-cli=={self.version} "
                f"for the stable channel"
            )

        return super().get_build_script(build)
