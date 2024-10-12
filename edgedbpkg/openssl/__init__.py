from __future__ import annotations

import pathlib
import platform
import re
import shlex

from metapkg import packages
from metapkg import targets


class OpenSSL(packages.BundledCPackage):
    title = "OpenSSL"
    name = packages.canonicalize_name("openssl")
    aliases = ["openssl-dev"]

    _server = "https://www.openssl.org/source/"

    sources = [
        {
            "url": _server + "/openssl-{version}.tar.gz",
            "csum_url": _server + "/openssl-{version}.tar.gz.sha256",
            "csum_algo": "sha256",
        }
    ]

    @property
    def supports_out_of_tree_builds(self) -> bool:
        return False

    def sh_get_configure_command(self, build: targets.Build) -> str:
        if self.supports_out_of_tree_builds:
            sdir = build.get_source_dir(self, relative_to="pkgbuild")
        else:
            sdir = build.get_build_dir(self, relative_to="pkgbuild")

        return shlex.quote(str(sdir / "Configure"))

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        conf_args = super().get_configure_args(build, wd=wd) | {
            "--prefix": build.get_install_prefix(self),
            "--openssldir": build.get_install_path(self, "sysconf") / "ssl",
            "--libdir": build.get_install_path(self, "lib"),
            "no-ssl3": None,
            "shared": None,
        }

        arch = build.target.machine_architecture
        if arch == "x86_64":
            if platform.system() == "Darwin":
                conf_args["darwin64-x86_64-cc"] = None
            conf_args["enable-ec_nistp_64_gcc_128"] = None
        elif arch == "aarch64":
            if platform.system() == "Darwin":
                conf_args["darwin64-arm64-cc"] = None
        else:
            raise RuntimeError(f"unexpected architecture: {arch}")

        if self.options.get("shared", True):
            conf_args["shared"] = None
        else:
            conf_args["no-shared"] = None
            conf_args["no-legacy"] = None

        return conf_args

    def get_configure_env(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        conf_env = super().get_configure_env(build, wd=wd)
        if platform.system() == "Darwin":
            # Force 64-bit build
            conf_env["KERNEL_BITS"] = "64"
        return conf_env

    def get_make_install_target(self, build: targets.Build) -> str:
        # Don't bother installing a gazillion of man pages.
        return "install_sw"

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

    @property
    def provides_build_tools(self) -> bool:
        return True

    def get_install_path(
        self,
        build: targets.Build,
        aspect: targets.InstallAspect,
    ) -> pathlib.Path | None:
        if aspect == "include":
            return build.get_install_prefix(self) / "include"
        else:
            return super().get_install_path(build, aspect)
