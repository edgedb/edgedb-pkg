from __future__ import annotations

import shlex

from metapkg import targets

from edgedbpkg import pgext


class StatStatements(pgext.PostgresCExtension):
    title = "edb_stat_statements extension"
    ident = "pgext-edb-stat-statements"
    description = "Query performance statistics extension"
    license_id = "PostgreSQL"
    group = "Applications/Databases"

    sources = []  # reuses edgedb-server source, see get_prepare_script

    artifact_build_requirements = [
        "postgresql-edgedb (>=17)",
    ]

    def get_prepare_script(self, build: targets.Build) -> str:
        source_dir = build.get_source_dir(
            build.get_package("edgedb-server"), relative_to="pkgbuild"
        )
        sdir = shlex.quote(str(source_dir / "edb_stat_statements"))
        return f"test ./ -ef {sdir} || cp -a {sdir}/* ./\n"

    def get_configure_script(self, build: targets.Build) -> str:
        return ""

    def get_build_script(self, build: targets.Build) -> str:
        pg_build_dir = build.get_build_dir(
            build.get_package("postgresql-edgedb"), relative_to="pkgbuild"
        )
        ddir = shlex.quote(str(pg_build_dir / "_install"))
        args = self.get_make_args(build)
        return "\n".join(
            [
                self.get_build_command(build, args),
                self.get_build_command(
                    build, args | {"DESTDIR": ddir}, "install"
                ),
            ]
        )
