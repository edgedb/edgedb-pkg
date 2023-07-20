from __future__ import annotations

from typing import TYPE_CHECKING

import pathlib

from poetry.core.packages import dependency as poetry_dep

from metapkg import packages
from metapkg import targets

from edgedbpkg.pgext import pgvector
from edgedbpkg import postgresql

if TYPE_CHECKING:
    from cleo.io import io as cleo_io


class PostgreSQLBundle(packages.BundledPackage):

    title = "PostgreSQL"
    name = "postgresql-bundle"
    group = "Applications/Databases"

    sources = [
        {
            "url": f"file://{pathlib.Path(__file__).parent.resolve() / 'bundle'}",
        },
    ]

    @classmethod
    def resolve(
        cls,
        io: cleo_io.IO,
        *,
        version: str | None = None,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
    ) -> PostgreSQLBundle:
        postgres = postgresql.PostgreSQL.resolve(
            io,
            version=version,
            revision=revision,
            is_release=is_release,
            target=target,
        )

        bundle = cls(
            version=postgres.version,
            pretty_version=postgres.pretty_version,
        )

        bundle.bundle_deps = [
            postgres,
            pgvector.PgVector("v0.4.2"),
        ]

        return bundle

    def get_requirements(self) -> list[poetry_dep.Dependency]:
        req_spec = [
            f"postgresql-edgedb (== {self.version})",
            "pgext-pgvector",
        ]

        reqs = []
        for item in req_spec:
            reqs.append(poetry_dep.Dependency.create_from_pep_508(item))

        return reqs

    def get_configure_script(self, build: targets.Build) -> str:
        return ""

    def get_build_script(self, build: targets.Build) -> str:
        return ""
