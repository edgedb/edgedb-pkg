from __future__ import annotations

from typing import TYPE_CHECKING

import pathlib

from poetry.core.packages import dependency as poetry_dep

from metapkg import packages
from metapkg import targets

from edgedbpkg.pgext import pgvector, postgis
from edgedbpkg import postgresql

if TYPE_CHECKING:
    from cleo.io import io as cleo_io


class PostgreSQLBundle(packages.BundledPackage):
    title = "PostgreSQL"
    name = packages.canonicalize_name("postgresql-bundle")
    group = "Applications/Databases"

    sources = [
        {
            "url": f"file://{pathlib.Path(__file__).parent.resolve() / 'bundle'}",
        },
    ]

    bundle_deps: list[packages.BundledPackage]

    artifact_requirements = {
        "<16.0": [
            "pgext-pgvector (== 0.4.2)",
        ],
        ">=16.0": [
            "pgext-pgvector (~= 0.6.0)",
            "pgext-postgis (~= 3.4.3)",
        ],
    }

    @classmethod
    def resolve(
        cls,
        io: cleo_io.IO,
        *,
        version: str | None = None,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
        requires: list[poetry_dep.Dependency] | None = None,
    ) -> PostgreSQLBundle:
        postgres = postgresql.PostgreSQL.resolve(
            io,
            version=version,
            revision=revision,
            is_release=is_release,
            target=target,
            requires=requires,
        )

        bundle = cls(
            version=postgres.version,
            pretty_version=postgres.pretty_version,
        )

        bundle.bundle_deps = [
            postgres,
            pgvector.PgVector("v0.4.2"),
            pgvector.PgVector("v0.6.0"),
            postgis.PostGIS("3.4.3"),
        ]

        return bundle

    def get_requirements(self) -> list[poetry_dep.Dependency]:
        reqs = super().get_requirements()
        reqs.append(
            poetry_dep.Dependency.create_from_pep_508(
                f"postgresql-edgedb (== {self.version})"
            ),
        )
        return reqs

    def get_build_script(self, build: targets.Build) -> str:
        return ""
