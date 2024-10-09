from __future__ import annotations

from metapkg import packages

from edgedbpkg import pgext


class PgVector(pgext.PostgresCExtension):
    title = "pgvector extension"
    name = packages.canonicalize_name("pgext-pgvector")
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
