from __future__ import annotations

import pathlib

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
        # FIXME: We should base it on the pinned version in edgedb-postgis,
        # or something like that. auto is broken on non-tagged builds currently.
        return '3.5.1'
        # return edgedb_ext.PGEXT_VERSION_AUTO

    def get_make_install_destdir_subdir(
        self,
        build: targets.Build,
    ) -> pathlib.Path:
        if build.target.is_portable():
            return build.get_rel_install_prefix(self)
        else:
            return super().get_make_install_destdir_subdir(build)


# EdgeQL-only version of the above
class PostGISEdgeQL(PostGIS):
    ident = "edbext-postgis-edgeql"

    @classmethod
    def get_pgext_ver(cls) -> str | None:
        return None

    @classmethod
    def is_universal(cls) -> bool:
        return True
