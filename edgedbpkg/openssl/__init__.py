from __future__ import annotations
from typing import *

import platform
import re
import shlex
import textwrap

from metapkg import packages
from metapkg import targets


class OpenSSL(packages.BundledCPackage):

    title = "OpenSSL"
    name = "openssl"
    aliases = ["openssl-dev"]

    _server = "https://www.openssl.org/source/"

    sources = [
        {
            "url": _server + "/openssl-{version}.tar.gz",
            "csum_url": _server + "/openssl-{version}.tar.gz.sha256",
            "csum_algo": "sha256",
        }
    ]

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = shlex.quote(
            str(build.get_source_dir(self, relative_to="pkgbuild"))
        )
        copy_sources = f"test ./ -ef {sdir} || cp -a {sdir}/* ./"

        configure = "./config"
        configure_flags = {
            "--openssldir": str(
                build.get_full_install_prefix() / "etc" / "ssl"
            ),
            "no-ssl2": None,
            "no-ssl3": None,
            "shared": None,
            "enable-ec_nistp_64_gcc_128": None,
        }

        cfgcmd = self.sh_configure(build, configure, configure_flags)
        if platform.system() == "Darwin":
            # Force 64-bit build
            cfgcmd = f"KERNEL_BITS=64 {cfgcmd}"

        return "\n\n".join(
            [
                copy_sources,
                cfgcmd,
            ]
        )

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        installdest = build.get_install_dir(self, relative_to="pkgbuild")
        make = build.sh_get_command("make")

        return script + textwrap.dedent(
            f"""\
            {make} DESTDIR=$(pwd)/"{installdest}" install_sw
            """
        )

    @classmethod
    def from_upstream_version(cls, version: str) -> OpenSSL:
        pat = r"(?P<ver>(\d+)(\.(\d+))*)(?P<patchver>[a-z]?)"
        if m := re.match(pat, version):
            if m.group("patchver"):
                pep440_version = f"{m.group('ver')}.{ord(m.group('patchver'))}"
            else:
                pep440_version = m.group("ver")
        else:
            raise ValueError(
                f"OpenSSL version does not match expected pattern: {version}"
            )

        return OpenSSL(pep440_version, source_version=version)

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["ssl", "crypto"]
