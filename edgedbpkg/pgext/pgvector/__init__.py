from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
)

import re
import shlex

from poetry.core.constraints import version as poetry_version

from metapkg import packages
from metapkg import targets

from edgedbpkg import postgresql

if TYPE_CHECKING:
    from cleo.io import io as cleo_io


class PgVector(packages.BundledCPackage):
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

    # Populated in resolve() when this is built as top-level package.
    bundle_deps: list[packages.BundledPackage] = []

    @classmethod
    def resolve(
        cls,
        io: cleo_io.IO,
        *,
        version: str | None = None,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
    ) -> PgVector:
        slot: int | None = None
        if version is not None:
            ver = poetry_version.Version.parse(version)
            if ver.epoch != 0:
                slot = ver.epoch
                version = f"v{ver.replace(epoch=0).to_string()}"

        if slot is not None:
            pg_ver = str(slot)
        else:
            pg_ver = "15"

        cls.bundle_deps.append(postgresql.PostgreSQL(version=pg_ver))

        pgvector = super().resolve(
            io,
            version=version,
            revision=revision,
            is_release=is_release,
            target=target,
        )

        if slot is not None:
            pgvector.set_slot(str(slot))

        return pgvector

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._slot = ""

    def set_slot(self, slot: str) -> None:
        self._slot = slot

    @property
    def slot(self) -> str:
        return self._slot

    def version_includes_slot(self) -> bool:
        return False

    def get_configure_script(self, build: targets.Build) -> str:
        srcdir = build.get_source_dir(self, relative_to="pkgbuild")
        sdir = shlex.quote(str(srcdir))
        copy_sources = f"test ./ -ef {sdir} || cp -a {sdir}/* ./"

        return copy_sources

    def get_make_env(self, build: targets.Build, wd: str) -> str:
        return build.sh_format_args(
            {
                "PG_CONFIG": build.sh_get_command("pg_config"),
                "USE_PGXS": "1",
            },
            linebreaks=False,
            force_args_eq=True,
        )

    def get_make_install_env(self, build: targets.Build, wd: str) -> str:
        return build.sh_format_args(
            {
                "PG_CONFIG": build.sh_get_command("pg_config_install"),
                "USE_PGXS": "1",
            },
            linebreaks=False,
            force_args_eq=True,
        )

    def get_patches(self) -> dict[str, list[tuple[str, str]]]:
        v = f"{self.version.major}{self.version.minor}"

        patches = dict(super().get_patches())
        for pkg, pkg_patches in patches.items():
            if pkg == self.name:
                filtered = []
                for i, (pn, pfile) in enumerate(list(pkg_patches)):
                    m = re.match(r"^.*-(\d+)$", pn)
                    if m and m.group(1) != v:
                        pass
                    else:
                        filtered.append((pn, pfile))
                patches[pkg] = filtered
                break

        return patches
