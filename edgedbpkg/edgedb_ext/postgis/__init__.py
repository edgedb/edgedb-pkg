from __future__ import annotations

import pathlib

from metapkg import packages
from metapkg import targets

from edgedbpkg import edgedb_ext


class PostGIS(edgedb_ext.EdgeDBExtension):
    title = "edgedb postgis extension"
    ident = "edbext-postgis"
    description = "Geographic Objects for EdgeDB"
    license_id = "GPL-3"
    group = "Applications/Databases"

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb-postgis.git",
            "extras": {
                "exclude_submodules": ["postgis"],
            },
        },
    ]

    @classmethod
    def get_pgext_ver(cls) -> str | None:
        return "3.4.3"

    def get_make_install_destdir_subdir(
        self,
        build: targets.Build,
    ) -> pathlib.Path:
        if build.target.is_portable():
            return build.get_rel_install_prefix(self)
        else:
            return super().get_make_install_destdir_subdir(build)
