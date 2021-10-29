from __future__ import annotations

import pathlib
import platform
import re
import textwrap

from metapkg import packages
from metapkg import targets

from edgedbpkg import icu, openssl


class PostgreSQL(packages.BundledCPackage):

    title = "PostgreSQL"
    name = "postgresql-edgedb"

    sources = (
        {
            "url": "git+https://github.com/postgres/postgres.git",
        },
    )

    artifact_requirements = [
        "icu (>=50)",
        "openssl (>=1.1.1)",
        "pam",
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
        "pam-dev",
        "uuid-dev",
        "zlib-dev",
    ]

    bundle_deps = [
        openssl.OpenSSL("3.0.0"),
        icu.ICU("69.1"),
    ]

    @classmethod
    def to_vcs_version(cls, version: str) -> str:
        return f"REL_{version.replace('.', '_')}"

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

    def get_configure_script(self, build: targets.Build) -> str:
        extra_version = ""

        system = platform.system()
        if system.endswith("BSD"):
            uuid_lib = "bsd"
        elif system == "Linux" or system == "Darwin":
            # macOS actually ships the e2fs version despite being a "BSD"
            uuid_lib = "e2fs"
        else:
            raise NotImplementedError(f"unsupported target system: {system}")

        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        configure = sdir / "configure"

        configure_flags: dict[str, str | pathlib.Path | None] = {
            "--sysconfdir": build.get_install_path("sysconf"),
            "--datarootdir": build.get_install_path("data"),
            "--bindir": build.get_install_path("bin"),
            "--libdir": build.get_install_path("lib"),
            "--includedir": build.get_install_path("include"),
            "--with-extra-version": extra_version,
            "--with-icu": None,
            "--without-pam": None,
            "--without-zlib": None,
            "--with-openssl": None,
            "--with-uuid": uuid_lib,
            "--without-readline": None,
        }

        icu_pkg = build.get_package("icu")
        if build.is_bundled(icu_pkg):
            icu_path = build.get_install_dir(icu_pkg, relative_to="pkgbuild")
            icu_path /= build.get_full_install_prefix().relative_to("/")
            icu_rel_path = f'$(pwd)/"{icu_path}"'
            configure_flags["ICU_CFLAGS"] = f"!-I{icu_rel_path}/include/"
            icu_ldflags = build.sh_get_bundled_shlib_ldflags(
                icu_pkg, relative_to="pkgbuild"
            )
            configure_flags["ICU_LIBS"] = f"!{icu_ldflags}"

        uuid_pkg = build.get_package("uuid")
        if build.is_bundled(uuid_pkg):
            uuid_path = build.get_install_dir(uuid_pkg, relative_to="pkgbuild")
            uuid_path /= build.get_full_install_prefix().relative_to("/")
            uuid_rel_path = f'$(pwd)/"{uuid_path}"'
            configure_flags["UUID_CFLAGS"] = f"!-I{uuid_rel_path}/include/"
            uuid_ldflags = build.sh_get_bundled_shlib_ldflags(
                uuid_pkg, relative_to="pkgbuild"
            )
            configure_flags["UUID_LIBS"] = f"!{uuid_ldflags}"

        openssl_pkg = build.get_package("openssl")
        if build.is_bundled(openssl_pkg):
            openssl_root = build.get_install_dir(
                openssl_pkg, relative_to="pkgbuild"
            )
            openssl_path = (
                openssl_root / build.get_full_install_prefix().relative_to("/")
            )
            openssl_rel_path = f'$(pwd)/"{openssl_path}"'
            configure_flags[
                "OPENSSL_CFLAGS"
            ] = f"!-I{openssl_rel_path}/include/"
            openssl_ldflags = build.sh_get_bundled_shlib_ldflags(
                openssl_pkg, relative_to="pkgbuild"
            )
            configure_flags["OPENSSL_LIBS"] = f"!{openssl_ldflags}"

            ldflags = f"!-L{openssl_rel_path}/lib"

            if system == "Darwin":
                # ./configure tries to compile and test a program
                # and it fails because openssl is not yet installed
                # at its install_name location.
                configure_flags["DYLD_FALLBACK_LIBRARY_PATH"] = openssl_root
            else:
                ldflags += f'" "-Wl,-rpath-link,{openssl_rel_path}/lib'

            configure_flags["LDFLAGS"] = ldflags

        if build.target.has_capability("tzdata"):
            zoneinfo = build.target.get_resource_path(build, "tzdata")
            configure_flags["--with-system-tzdata"] = zoneinfo

        if build.target.has_capability("systemd"):
            configure_flags["--with-systemd"] = None

        if (
            build.extra_optimizations_enabled()
            and build.supports_lto()
            and build.uses_modern_gcc()
        ):
            configure_flags["CFLAGS"] = "!" + " ".join(
                (
                    "-flto",
                    "-fuse-linker-plugin",
                    "-ffat-lto-objects",
                    "-flto-partition=none",
                )
            )

        return self.sh_configure(build, configure, configure_flags)

    def get_build_script(self, build: targets.Build) -> str:
        make = build.sh_get_command("make")

        wrapper_path = pathlib.Path("_install") / "pg_config_wrapper"
        wrapper_cmd = build.sh_get_command(
            "pg_config_wrapper", relative_to="pkgbuild"
        )

        bash = build.sh_get_command("bash")
        make_pg_config_wrapper = textwrap.dedent(
            f"""\
            echo '#!{bash}' >> "{wrapper_path}"
            echo 'set -ex' >> "{wrapper_path}"
            echo 'pushd "$(dirname $0)/../" >/dev/null' >> "{wrapper_path}"
            echo '{wrapper_cmd}' '"${{@}}"' >> "{wrapper_path}"
            echo 'popd >/dev/null' >> "{wrapper_path}"
            chmod +x "{wrapper_path}"
        """
        )

        return textwrap.dedent(
            f"""\
            {make}
            {make} -C contrib
            {make} DESTDIR=$(pwd)/_install install
            {make} -C contrib DESTDIR=$(pwd)/_install install
            {make_pg_config_wrapper}
        """
        )

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        installdest = build.get_install_dir(self, relative_to="pkgbuild")
        make = build.sh_get_command("make")

        return script + textwrap.dedent(
            f"""\
            {make} DESTDIR=$(pwd)/"{installdest}" install
            {make} DESTDIR=$(pwd)/"{installdest}" -C contrib install
            """
        )

    def get_build_tools(self, build: targets.Build) -> dict[str, pathlib.Path]:
        bindir = build.get_install_path("bin").relative_to("/")
        datadir = build.get_install_path("data")
        libdir = build.get_install_path("lib")
        temp_install_path = build.get_build_dir(self) / "_install"

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
                pathlib.Path(__file__).parent.parent.parent /
                '{temp_install_path}'
            ).resolve()

            pgc = path / '{bindir}' / 'pg_config'

            proc = subprocess.run(
                [pgc] + sys.argv[1:],
                check=True, stdout=subprocess.PIPE,
                universal_newlines=True)

            for line in proc.stdout.split('\\n'):
                if ('{datadir}' in line or
                        ('{libdir}' in line and 'pgxs' not in line)):
                    line = line.replace(str(path), '')
                print(line)
        """
        )

        wrapper_cmd = build.write_helper(
            "pg_config_wrapper.py", wrapper, relative_to="sourceroot"
        )

        return {
            "pg_config_wrapper": wrapper_cmd,
            "pg_config": temp_install_path / "pg_config_wrapper",
        }
