from __future__ import annotations

import shlex
import textwrap

from metapkg import packages
from metapkg import targets


class HAProxyDataPlaneAPI(packages.BundledPackage):

    title = "HAProxy Data Plane API"
    name = "haproxy-dataplane-api"

    sources = [
        {
            "url": "git+https://github.com/haproxytech/dataplaneapi.git",
            "extras": {
                "include_gitdir": True,
            },
        },
    ]

    def get_package_layout(
        self, build: targets.Build
    ) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.FLAT

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = shlex.quote(
            str(build.get_source_dir(self, relative_to="pkgbuild"))
        )
        copy_sources = f"test ./ -ef {sdir} || cp -a {sdir}/* ./"
        return copy_sources

    def get_build_script(self, build: targets.Build) -> str:
        make = build.sh_get_command("make")
        return f"{make} build"

    def get_build_install_script(self, build: targets.Build) -> str:
        installdest = build.get_install_dir(self, relative_to="pkgbuild")
        bindir = build.get_install_path("bin").relative_to("/")
        dest = installdest / bindir / "haproxy-dataplane-api"
        return textwrap.dedent(
            f"""\
            mkdir -p "$(dirname "{dest}")"
            cp -a build/dataplaneapi "{dest}"
            """
        )
