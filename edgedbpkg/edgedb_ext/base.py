from __future__ import annotations
from typing import (
    TYPE_CHECKING,
)

import dataclasses
import importlib
import pathlib

from poetry.core.packages import dependency as poetry_dep
from poetry.core.constraints import version as poetry_version

from metapkg import packages
from metapkg import targets

from edgedbpkg import edgedb
from edgedbpkg import pgext

if TYPE_CHECKING:
    from cleo.io import io as cleo_io

EXTS_MK = (
    "https://raw.githubusercontent.com/edgedb/edgedb/refs/heads/master"
    + "/tests/extension-testing/exts.mk"
)


class EdgeDBExtension(packages.BuildSystemMakePackage):
    # Populated in resolve() when this is built as top-level package.
    bundle_deps: list[packages.BundledPackage] = []
    _edb: edgedb.EdgeDB
    _pgext: poetry_dep.Dependency

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
    ) -> EdgeDBExtension:
        server_slot = ""
        if version is not None:
            server_slot, _, version = version.rpartition("!")

        if not server_slot:
            raise RuntimeError(
                "must specify EdgeDB version as epoch, eg 5!1.0"
            )

        edb_ver = poetry_version.Version.parse(server_slot)
        if edb_ver.minor is None:
            edb_ver = edb_ver.replace(
                release=dataclasses.replace(edb_ver.release, minor=0),
            )

        edb = edgedb.EdgeDB.resolve(
            io,
            version=str(edb_ver),
            is_release=edb_ver.dev is None,
            target=target,
        )

        if requires is None:
            requires = []
        else:
            requires = list(requires)

        pgext_ver = cls.get_pgext_ver()

        pg_ext: pgext.PostgresCExtension | None
        if pgext_ver:
            # Find the postgres version
            for dep in edb.get_requirements():
                if dep.name == "postgresql-edgedb":
                    pg = packages.get_bundled_pkg(dep)
                    break
            else:
                raise RuntimeError(
                    "could not determine version of PostgreSQL used "
                    "by the specified EdgeDB version"
                )

            pgextname = cls.ident.replace("edbext-", "pgext-")
            requires.append(
                poetry_dep.Dependency.create_from_pep_508(
                    f"{pgextname} (== {pgext_ver})",
                ),
            )
            _, _, mod = cls.__module__.rpartition(".")
            pg_ext = getattr(
                importlib.import_module(f"edgedbpkg.pgext.{mod}"),
                cls.__name__,
            )(pgext_ver)
            assert pg_ext is not None
            pg_ext.build_requires.append(pg.to_dependency())

        else:
            pg_ext = None

        if name is None:
            pkgname = cls.ident.removeprefix("edbext-")
        else:
            pkgname = str(name)

        name = packages.canonicalize_name(f"{edb.name_slot}-{pkgname}")

        ext = super().resolve(
            io,
            name=name,
            version=version,
            revision=revision,
            is_release=is_release,
            target=target,
            requires=requires,
        )
        ext._edb = edb

        if pg_ext is not None:
            ext.bundle_deps.append(pg_ext)

        return ext

    @classmethod
    def _get_sources(cls, version: str | None) -> list[packages.BaseSource]:
        srcs = super()._get_sources(version)
        srcs.append(
            packages.HttpsSource(EXTS_MK, name="exts.mk", archive=None)
        )
        return srcs

    @classmethod
    def get_pgext_ver(cls) -> str | None:
        return None

    @property
    def supports_out_of_tree_builds(self) -> bool:
        return False

    def get_build_script(self, build: targets.Build) -> str:
        return ""

    def get_dep_install_subdir(
        self,
        build: targets.Build,
        pkg: packages.BasePackage,
    ) -> pathlib.Path:
        prefix = build.get_install_prefix(self)
        lib_dir = build.get_install_path(self, "lib").relative_to(prefix)
        if pkg.name not in {"postgresql-edgedb", "edgedb-server"}:
            return lib_dir / "postgresql" / self.unique_name
        else:
            return pathlib.Path("")

    def get_make_args(self, build: targets.Build) -> packages.Args:
        return super().get_make_args(build) | {
            "MKS": "exts.mk",
            "WITH_SQL": "no",
            "WITH_EDGEQL": "yes",
        }

    def get_make_install_args(self, build: targets.Build) -> packages.Args:
        return super().get_make_args(build) | {
            "MKS": "exts.mk",
            "WITH_SQL": "no",
            "WITH_EDGEQL": "yes",
        }

    def get_root_install_subdir(self, build: targets.Build) -> pathlib.Path:
        if build.target.is_portable():
            return pathlib.Path(self.name_slot)
        else:
            return pathlib.Path(self._edb.name_slot)

    def get_make_install_destdir_subdir(
        self,
        build: targets.Build,
    ) -> pathlib.Path:
        if build.target.is_portable():
            return pathlib.Path("")
        else:
            return (
                build.get_install_path(self._edb, "data").relative_to("/")
                / "data"
                / "extensions"
                / f"{self.pretty_name}-{self.version}"
            )
