from __future__ import annotations

import pathlib
import platform
import re
import textwrap

from poetry.core.constraints import version as poetry_version

from metapkg import packages
from metapkg import targets

from edgedbpkg import icu, libuuid, openssl, zlib


class PostgreSQL(packages.BundledCAutoconfPackage):
    title = "PostgreSQL"
    name = packages.canonicalize_name("postgresql-edgedb")
    group = "Applications/Databases"

    _pftp = "https://ftp.postgresql.org/pub/source/v{version}/"

    sources = [
        {
            "url": _pftp + "postgresql-{version}.tar.bz2",
            "csum_url": _pftp + "postgresql-{version}.tar.bz2.sha256",
            "csum_algo": "sha256",
        }
    ]

    artifact_requirements = [
        "icu (>=50)",
        "openssl (>=1.1.1)",
        "uuid",
        "zlib",
        'tzdata; extra == "capability-tzdata"',
    ]

    artifact_build_requirements = [
        "bison",
        "flex",
        "perl",
        'systemd-dev ; extra == "capability-systemd"',
        "icu-dev (>=50)",
        "openssl-dev (>=1.1.1)",
        "uuid-dev",
        "zlib-dev",
    ]

    bundle_deps = [
        icu.ICU("74.1"),
        libuuid.LibUUID("2.39.3"),
        openssl.OpenSSL("3.1.5"),
        zlib.Zlib("1.3.1"),
    ]

    @classmethod
    def to_vcs_version(cls, version: str) -> str:
        parts = version.split(".")
        if len(parts) == 1:
            return f"REL_{version}_STABLE"
        else:
            return f"REL_{version.replace('.', '_')}"

    @classmethod
    def parse_vcs_version(cls, version: str) -> poetry_version.Version:
        if version.startswith("REL_"):
            v = (
                version.removeprefix("REL_")
                .removesuffix("_STABLE")
                .replace("_", ".")
            )
            return super().parse_vcs_version(v)
        else:
            return super().parse_vcs_version(version)

    def get_patches(self) -> dict[str, list[tuple[str, str]]]:
        patches = dict(super().get_patches())
        for pkg, pkg_patches in patches.items():
            if pkg == self.name:
                filtered = []
                for i, (pn, pfile) in enumerate(list(pkg_patches)):
                    m = re.match(r"^.*-(\d+)$", pn)
                    if m and int(m.group(1)) != self.version.major:
                        pass
                    else:
                        filtered.append((pn, pfile))
                patches[pkg] = filtered
                break

        return patches

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        extra_version = ""

        system = platform.system()
        if system.endswith("BSD"):
            uuid_lib = "bsd"
        elif system == "Linux" or system == "Darwin":
            # macOS actually ships the e2fs version despite being a "BSD"
            uuid_lib = "e2fs"
        else:
            raise NotImplementedError(f"unsupported target system: {system}")

        conf_args = super().get_configure_args(build, wd=wd) | {
            "--with-extra-version": extra_version,
            "--with-icu": None,
            "--without-pam": None,
            "--with-openssl": None,
            "--with-uuid": uuid_lib,
            "--without-readline": None,
        }

        if build.target.has_capability("tzdata"):
            zoneinfo = build.target.get_resource_path(build, "tzdata")
            conf_args["--with-system-tzdata"] = zoneinfo

        if build.target.has_capability("systemd"):
            conf_args["--with-systemd"] = None

        if (
            build.extra_optimizations_enabled()
            and build.supports_lto()
            and build.uses_modern_gcc()
        ):
            build.sh_append_flags(
                conf_args,
                "CFLAGS",
                (
                    "-flto",
                    "-fuse-linker-plugin",
                    "-ffat-lto-objects",
                    "-flto-partition=none",
                ),
            )

        return conf_args

    def get_build_script(self, build: targets.Build) -> str:
        args = self.get_make_args(build)
        ddir = '!"${_wd}"/_install'
        return "\n".join(
            [
                self.get_build_command(build, args),
                self.get_build_command(
                    build, args | {"--directory": "contrib"}
                ),
                self.get_build_command(
                    build, args | {"DESTDIR": ddir}, "install"
                ),
                self.get_build_command(
                    build,
                    args | {"--directory": "contrib", "DESTDIR": ddir},
                    "install",
                ),
            ]
        )

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        args = self.get_make_install_args(build) | {"--directory": "contrib"}
        script += "\n" + self.get_build_install_command(build, args, "install")
        return script

    def get_build_tools(self, build: targets.Build) -> dict[str, pathlib.Path]:
        bindir = build.get_install_path(self, "bin").relative_to("/")
        datadir = build.get_install_path(self, "data")
        docdir = build.get_install_path(self, "doc")
        libdir = build.get_install_path(self, "lib")
        includedir = build.get_install_path(self, "include")
        builddir_hlp = build.get_build_dir(self, relative_to="helpers")

        # Since we are using a temporary Postgres installation,
        # pg_config will return paths together with the temporary
        # installation prefix, so we need to wrap it to strip
        # it from certain paths.
        wrapper = textwrap.dedent(
            f"""\
            import pathlib
            import subprocess
            import sys

            path = (
                pathlib.Path(__file__).parent / "{builddir_hlp}" / "_install"
            ).resolve()

            pgc = path / "{bindir}" / "pg_config"

            proc = subprocess.run(
                [pgc] + sys.argv[1:],
                check=True, stdout=subprocess.PIPE,
                universal_newlines=True)

            for line in proc.stdout.split('\\n'):
                if ('{datadir}' in line or
                        '{docdir}' in line or
                        ('{libdir}' in line and 'pgxs' not in line)):
                    line = line.replace(str(path), '')
                print(line)
        """
        )

        wrapper_cmd = build.sh_write_python_helper(
            "pg_config_wrapper.py",
            wrapper,
            relative_to="pkgbuild",
            helper_path_relative_to="sourceroot",
        )

        # Same, but for install-time, so includes more paths
        wrapper = textwrap.dedent(
            f"""\
            import pathlib
            import subprocess
            import sys

            path = (
                pathlib.Path(__file__).parent / "{builddir_hlp}" / "_install"
            ).resolve()

            pgc = path / "{bindir}" / "pg_config"

            proc = subprocess.run(
                [pgc] + sys.argv[1:],
                check=True, stdout=subprocess.PIPE,
                universal_newlines=True)

            for line in proc.stdout.split('\\n'):
                if ('{datadir}' in line or
                        '{docdir}' in line or
                        '{includedir}' in line or
                        ('{libdir}' in line and 'pgxs' not in line)):
                    line = line.replace(str(path), '')
                print(line)
        """
        )

        install_wrapper_cmd = build.sh_write_python_helper(
            "pg_config_install_wrapper.py",
            wrapper,
            relative_to="pkgbuild",
            helper_path_relative_to="sourceroot",
        )

        return {
            "pg_config": pathlib.Path(wrapper_cmd),
            "pg_config_install": pathlib.Path(install_wrapper_cmd),
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return [
            "pq",
        ]
