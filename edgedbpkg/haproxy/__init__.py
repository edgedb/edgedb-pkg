from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Dict,
)

import pathlib
import shlex

from poetry.core.semver import version as poetry_version

from metapkg import tools
from metapkg import packages
from metapkg import targets

from edgedbpkg import libpcre2
from edgedbpkg import openssl

if TYPE_CHECKING:
    from cleo.io import io as cleo_io


class HAProxy(packages.BundledCPackage):

    title = "HAProxy"
    name = "haproxy"
    description = "A TCP/HTTP reverse proxy for high availability environments"
    license = "GPL-2"
    group = "Applications/Databases"

    sources = (
        {
            "url": "git+https://git.haproxy.org/git/haproxy{stable}.git",
        },
    )

    artifact_requirements = [
        "openssl (>=1.1.1)",
        "libpcre2",
    ]

    artifact_build_requirements = [
        "openssl-dev (>=1.1.1)",
        "libpcre2-dev",
    ]

    bundle_deps = [
        openssl.OpenSSL("3.0.2", options=dict(shared=False, static=True)),
        libpcre2.LibPCRE2("10.40", options=dict(shared=False, static=True)),
    ]

    def get_package_layout(
        self, build: targets.Build
    ) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.FLAT

    def get_license_files_pattern(self) -> str:
        return ""

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = shlex.quote(
            str(build.get_source_dir(self, relative_to="pkgbuild"))
        )
        return f"test ./ -ef {sdir} || cp -a {sdir}/* ./"

    def get_build_script(self, build: targets.Build) -> str:
        make_flags: Dict[str, str | pathlib.Path | None] = {
            "USE_OPENSSL": "1",
            "USE_STATIC_PCRE2": "1",
            "USE_PCRE2_JIT": "1",
            "USE_LIBCRYPT": "",
            "USE_TFO": "1",
            "USE_NS": "1",
            "PREFIX": str(build.get_full_install_prefix()),
            "TARGET": "linux-glibc",
        }

        openssl_pkg = build.get_package("openssl")
        if build.is_bundled(openssl_pkg):
            openssl_root = build.get_install_dir(
                openssl_pkg, relative_to="pkgbuild"
            )
            openssl_path = (
                openssl_root / build.get_full_install_prefix().relative_to("/")
            )
            openssl_rel_path = f'$(pwd)/"{openssl_path}"'
            make_flags["SSL_INC"] = f"!{openssl_rel_path}/include/"
            make_flags["SSL_LIB"] = f"!{openssl_rel_path}/lib/"

        libpcre2_pkg = build.get_package("libpcre2")
        if build.is_bundled(libpcre2_pkg):
            libpcre2_root = build.get_install_dir(
                libpcre2_pkg, relative_to="pkgbuild"
            )
            libpcre2_path = (
                libpcre2_root
                / build.get_full_install_prefix().relative_to("/")
            )
            libpcre2_rel_path = f'$(pwd)/"{libpcre2_path}"'
            make_flags["PCRE2DIR"] = f"!{libpcre2_rel_path}"

        make_flags = build.sh_append_global_flags(
            make_flags, flag_names={"CFLAGS": "CPU_CFLAGS"}
        )
        build.sh_append_run_time_ldflags(make_flags, self)

        return build.sh_get_command(
            "make", args=make_flags, force_args_eq=True
        )

    def get_build_install_script(self, build: targets.Build) -> str:
        installdest = build.get_install_dir(self, relative_to="pkgbuild")
        make_flags = {
            "DESTDIR": f'!$(pwd)"/{installdest}"',
            "SBINDIR": str(build.get_install_path("bin")),
            "MANDIR": str(build.get_install_path("data") / "man"),
            "DOCDIR": str(build.get_install_path("data") / "doc"),
        }
        return (
            build.sh_get_command("make", args=make_flags, force_args_eq=True)
            + " install"
        )

    @classmethod
    def version_from_vcs_version(
        cls,
        io: cleo_io.IO,
        repo: tools.git.Git,
        vcs_version: str,
        is_release: bool,
    ) -> str:
        ver = repo.run("describe", "--tags", vcs_version).strip()
        if ver.startswith("v"):
            ver = ver[1:]

        parts = ver.split("-")
        ver = parts[0]
        if len(parts) > 1 and parts[1].startswith("dev"):
            ver += f".{parts[1]}"
            offset = 2
        else:
            offset = 1

        local = ".".join(parts[offset + 1 :])
        if local:
            ver += f"+{local}"

        return ver

    @classmethod
    def get_source_url_variables(cls, version: str) -> dict[str, str]:
        if version.startswith("v"):
            base_ver = poetry_version.Version.parse(version)
            stable = f"-{base_ver.major}.{base_ver.minor}"
        else:
            stable = ""
        return {"stable": stable}
