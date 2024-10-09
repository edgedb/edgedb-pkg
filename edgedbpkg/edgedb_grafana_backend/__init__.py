from __future__ import annotations
from typing import TYPE_CHECKING

import textwrap

from metapkg import packages

if TYPE_CHECKING:
    from metapkg import targets

from edgedbpkg import mage


class EdgeDBGrafanaBackend(packages.BundledPackage):
    title = "EdgeDB Grafana Backend"
    name = packages.canonicalize_name("edgedb-grafana-backend")

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb-grafana-backend.git",
        },
    ]

    artifact_build_requirements = [
        "mage",
    ]

    bundle_deps = [
        mage.Mage("v1.15.0"),
    ]

    @property
    def supports_out_of_tree_builds(self) -> bool:
        return False

    def get_build_script(self, build: targets.Build) -> str:
        gopath = build.get_temp_dir(self, relative_to="pkgbuild")
        return textwrap.dedent(
            f"""\
            export PATH="$(pwd)/{gopath}/bin:${{PATH}}"
            {build.sh_get_command("mage")} build:backend
            yarn install && yarn build
            """
        )

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        installdest = build.get_build_install_dir(
            self, relative_to="pkgbuild"
        ) / build.get_rel_install_prefix(self)
        return textwrap.dedent(
            f"""\
            {script}
            mkdir -p "$(dirname "{installdest}")"
            cp -a dist "{installdest}"
            """
        )

    def get_package_layout(
        self,
        build: targets.Build,
    ) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.REGULAR
