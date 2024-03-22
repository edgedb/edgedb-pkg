from __future__ import annotations
from typing import TYPE_CHECKING

import pathlib
import textwrap

from metapkg import packages

if TYPE_CHECKING:
    from metapkg import targets


class Mage(packages.BundledGoPackage):
    title = "Mage"
    name = packages.canonicalize_name("mage")

    sources = [
        {
            "url": "git+https://github.com/magefile/mage.git",
        },
    ]

    def get_build_script(self, build: targets.Build) -> str:
        gopath = build.get_temp_dir(self, relative_to="pkgbuild")
        return textwrap.dedent(
            f"""\
            ls -l
            export PATH="$(pwd)/{gopath}/bin:${{PATH}}"
            export GOOS=$(go env GOOS)
            export GOARCH=$(go env GOARCH)
            mkdir -p mage
            go build -o bin/mage
            """
        )

    def get_build_tools(self, build: targets.Build) -> dict[str, pathlib.Path]:
        build_dir = build.get_build_dir(self)
        return {"mage": build_dir / "bin" / "mage"}
