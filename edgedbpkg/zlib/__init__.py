from __future__ import annotations

from metapkg import packages
from metapkg import targets


class Zlib(packages.BundledCPackage):
    title = "zlib"
    name = packages.canonicalize_name("zlib")
    aliases = ["zlib-dev"]

    _server = "https://zlib.net/fossils/"

    sources = [
        {
            "url": _server + "zlib-{version}.tar.gz",
        }
    ]

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        configure = sdir / "configure"

        configure_flags = {
            "--prefix": str(build.get_full_install_prefix()),
        }

        return build.sh_format_command(configure, configure_flags)

    def get_build_script(self, build: targets.Build) -> str:
        global_flags = build.sh_append_global_flags()
        return build.sh_get_command(
            "make", args=global_flags, force_args_eq=True
        )

    def get_license_files_pattern(self) -> str:
        return "README"

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["z"]
