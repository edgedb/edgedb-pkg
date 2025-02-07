from __future__ import annotations
from typing import TYPE_CHECKING

import pathlib

from poetry.core.packages import dependency as poetry_dep

from metapkg import packages
from metapkg import targets
from metapkg.packages import python

from edgedbpkg import edgedb as edgedb_server

if TYPE_CHECKING:
    from cleo.io import io as cleo_io


python.set_python_runtime_dependency(
    poetry_dep.Dependency(
        name="python-edgedb",
        constraint=">=3.10.0,<3.13.0",
        allows_prereleases=True,
    )
)


class EdgeDBLanguageServer(edgedb_server.EdgeDBNoPostgres):
    title = "EdgeDBLanguageServer"
    ident = "edgedb-ls"
    description = "Language server for EdgeDB"
    identifier = "com.edgedb.edgedb-ls"

    # We don't need Postgres at all even at the build stage.
    artifact_build_requirements = packages.merge_requirements(
        edgedb_server.EdgeDBNoPostgres.common_build_reqs,
        edgedb_server.EdgeDBNoPostgres.python_requirements,
        edgedb_server.EdgeDBNoPostgres.libpg_query_reqs,
    )

    @classmethod
    def resolve(
        cls,
        io: cleo_io.IO,
        *,
        name: packages.NormalizedName | None = None,
        version: str | None = None,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
        requires: list[poetry_dep.Dependency] | None = None,
    ) -> EdgeDBLanguageServer:
        return (
            super()
            .resolve(
                io,
                name=name,
                version=version,
                revision=revision,
                is_release=is_release,
                target=target,
                requires=requires,
            )
            .with_features(["language-server"])
        )

    @property
    def slot(self) -> str:
        return ""

    def sh_get_build_wheel_env(
        self,
        build: targets.Build,
        *,
        site_packages: str,
        wd: str,
    ) -> packages.Args:
        return super().sh_get_build_wheel_env(
            build,
            site_packages=site_packages,
            wd=wd,
        ) | {"EDGEDB_BUILD_PACKAGE": "language-server"}

    def get_stdlib_bootstrap_script(self, build: targets.Build) -> str:
        return ""

    def get_stdlib_install_script(self, build: targets.Build) -> str:
        return ""

    def get_exposed_commands(self, build: targets.Build) -> list[pathlib.Path]:
        bindir = build.get_install_path(self, "bin")

        return [
            bindir / "edgedb-ls",
        ]

    def get_conflict_packages(
        self,
        build: targets.Build,
        root_version: str,
    ) -> list[str]:
        return ["edgedb-common"]
