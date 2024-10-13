from __future__ import annotations
from typing import (
    Dict,
)

import shlex

from metapkg import packages
from metapkg import targets

from edgedbpkg import zlib


class LibSQLite3(packages.BundledCAutoconfPackage):
    title = "libsqlite3"
    ident = "libsqlite3"
    aliases = ["libsqlite3-dev"]

    _server = "https://www.sqlite.org/2024/"

    sources = [
        {
            "url": _server + "sqlite-src-{sqlitever}.zip",
        }
    ]

    artifact_requirements = [
        "zlib",
    ]

    artifact_build_requirements = [
        "zlib-dev",
    ]

    bundle_deps = [
        zlib.Zlib("1.3.1"),
    ]

    @classmethod
    def get_source_url_variables(cls, version: str) -> Dict[str, str]:
        p = [int(v) for v in version.split(".")]
        if len(p) < 4:
            p.append(0)
        return {
            "sqlitever": "{p[0]:d}{p[1]:02d}{p[2]:02d}{p[3]:02d}".format(p=p)
        }

    @classmethod
    def get_dep_pkg_name(cls) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "SQLite3"

    @property
    def provides_build_tools(self) -> bool:
        return True

    def sh_get_configure_command(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        return f'/bin/sh {shlex.quote(str(sdir / "configure"))}'

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        conf_args = super().get_configure_args(build, wd=wd) | {
            "--enable-load-extension": None,
            "--enable-threadsafe": None,
            "--disable-static": None,
            "--enable-fts5": None,
            "--disable-editline": None,
            "--disable-readline": None,
            "--disable-tcl": None,
            "--disable-debug": None,
        }

        flags = [
            "SQLITE_ENABLE_API_ARMOR",
            "SQLITE_ENABLE_BYTECODE_VTAB",
            "SQLITE_ENABLE_COLUMN_METADATA",
            "SQLITE_ENABLE_DBPAGE_VTAB",
            "SQLITE_ENABLE_DBSTAT_VTAB",
            "SQLITE_ENABLE_DESERIALIZE",
            "SQLITE_ENABLE_EXPLAIN_COMMENTS",
            "SQLITE_ENABLE_FTS3",
            "SQLITE_ENABLE_FTS3_PARENTHESIS",
            "SQLITE_ENABLE_FTS4",
            "SQLITE_ENABLE_HIDDEN_COLUMNS",
            "SQLITE_ENABLE_MEMSYS5",
            "SQLITE_ENABLE_NORMALIZE",
            "SQLITE_ENABLE_OFFSET_SQL_FUNC",
            "SQLITE_ENABLE_PREUPDATE_HOOK",
            "SQLITE_ENABLE_RBU",
            "SQLITE_ENABLE_RTREE",
            "SQLITE_ENABLE_GEOPOLY",
            "SQLITE_ENABLE_SESSION",
            "SQLITE_ENABLE_STMT_SCANSTATUS",
            "SQLITE_ENABLE_STMTVTAB",
            "SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION",
            "SQLITE_ENABLE_UNLOCK_NOTIFY",
            "SQLITE_ENABLE_UPDATE_DELETE_LIMIT",
            "SQLITE_SOUNDEX",
            "SQLITE_USE_URI",
        ]

        build.sh_append_flags(
            conf_args,
            "CPPFLAGS",
            [f"-D{f}" for f in flags],
        )

        arch = build.target.machine_architecture
        if arch == "x86_64":
            build.sh_append_flags(
                conf_args,
                "CFLAGS",
                ("-mfpmath=sse",),
            )

        return conf_args

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["sqlite3"]
