from __future__ import annotations

from edgedbpkg import pgext

from metapkg import packages
from metapkg import targets


class PgVector(pgext.PostgresCExtension):
    title = "pgvector extension"
    ident = "pgext-pgvector"
    description = "Open-source vector similarity search for Postgres"
    license_id = "PostgreSQL"
    group = "Applications/Databases"

    sources = [
        {
            "url": "git+https://github.com/pgvector/pgvector.git",
        },
    ]

    artifact_build_requirements = [
        "postgresql-edgedb (>=13)",
    ]

    @property
    def supports_out_of_tree_builds(self) -> bool:
        return False

    def get_make_args(self, build: targets.Build) -> packages.Args:
        return super().get_make_args(build) | {
            "OPTFLAGS": "",
        }
