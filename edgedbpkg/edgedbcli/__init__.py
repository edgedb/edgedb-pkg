from __future__ import annotations
from typing import (
    Any,
)

import textwrap

from metapkg import packages
from metapkg import targets


class GelCLI(packages.BundledRustPackage):
    title = "GelCLI"
    ident = "gel-cli"
    description = "Gel Command Line Tools"
    license_id = "Apache-2.0"
    group = "Applications/Databases"
    url = "https://geldata.com/"

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb-cli.git",
        },
    ]

    @property
    def marketing_name(self) -> str:
        return "Gel"

    @property
    def marketing_slug(self) -> str:
        return "gel"

    def get_package_layout(
        self, build: targets.Build
    ) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.SINGLE_BINARY

    def get_license_files_patterns(self) -> list[str]:
        return []

    def get_artifact_metadata(self, build: targets.Build) -> dict[str, Any]:
        metadata = dict(super().get_artifact_metadata(build))
        metadata["publish_link_to_latest"] = ["gel-cli", "edgedb-cli"]
        return metadata

    def get_build_script(self, build: targets.Build) -> str:
        if build.channel == "stable" and not self.version.is_stable():
            raise AssertionError(
                f"cannot build non-stable gel-cli=={self.version} "
                f"for the stable channel"
            )

        return super().get_build_script(build)

    def get_transition_packages(
        self,
        build: targets.Build,
    ) -> list[str]:
        return ["edgedb-cli"]

    def get_prepare_script(self, build: targets.Build) -> str:
        script = super().get_prepare_script(build)
        sed = build.sh_get_command("sed")
        src = build.get_source_dir(self, relative_to="pkgbuild")
        script += textwrap.dedent(
            f"""\
            {sed} -i -e '/\\[\\[bin\\]\\]/,/\\[\\[.*\\]\\]/{{
                    s/^name\\s*=.*/name = "{self.marketing_slug}"/;
                }}' \\
                "{src}/Cargo.toml"
            """
        )
        return script

    def get_file_install_entries(self, build: targets.Build) -> list[str]:
        entries = list(super().get_file_install_entries(build))
        entries.append(f"{{systembindir}}/{self.marketing_slug}{{exesuffix}}")
        return entries


class EdgeDBCLI(GelCLI):
    title = "EdgeDBCLI"
    ident = "edgedb-cli"
    description = "EdgeDB Command Line Tools"
    url = "https://edgedb.com/"

    @property
    def marketing_name(self) -> str:
        return "EdgeDB"

    @property
    def marketing_slug(self) -> str:
        return "edgedb"

    def get_transition_packages(
        self,
        build: targets.Build,
    ) -> list[str]:
        return []
