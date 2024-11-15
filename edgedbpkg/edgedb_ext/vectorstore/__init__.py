from __future__ import annotations

import pathlib
from metapkg import targets
from edgedbpkg import edgedb_ext


class Vectorstore(edgedb_ext.EdgeDBExtension):
    title = "edgedb vectorstore extension"
    ident = "edbext-vectorstore"
    description = (
        "Premade types to use EdgeDB as a vectorstore with AI frameworks"
    )
    license_id = "Apache-2.0"
    group = "Applications/Databases"

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb-vectorstore.git",
            "extras": {},
        },
    ]

    def get_make_install_destdir_subdir(
        self,
        build: targets.Build,
    ) -> pathlib.Path:
        if build.target.is_portable():
            return build.get_rel_install_prefix(self)
        else:
            return super().get_make_install_destdir_subdir(build)
