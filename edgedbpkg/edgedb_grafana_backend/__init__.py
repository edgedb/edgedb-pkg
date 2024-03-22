from __future__ import annotations
from typing import TYPE_CHECKING

import shlex
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

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = shlex.quote(
            str(build.get_source_dir(self, relative_to="pkgbuild"))
        )
        copy_sources = f"test ./ -ef {sdir} || cp -a {sdir}/* ./"
        return copy_sources

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
        installdest = build.get_install_dir(
            self, relative_to="pkgbuild"
        ) / build.get_full_install_prefix().relative_to("/")
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
