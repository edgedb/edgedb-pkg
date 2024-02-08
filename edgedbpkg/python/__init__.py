from __future__ import annotations

import pathlib
import platform
import re
import textwrap

from poetry.core.semver import version as poetry_version

from metapkg import packages
from metapkg import targets

from edgedbpkg import libb2
from edgedbpkg import libffi
from edgedbpkg import libuuid
from edgedbpkg import openssl
from edgedbpkg import zlib


class Python(packages.BundledCPackage):
    title = "Python"
    name = packages.canonicalize_name("python-edgedb")

    _pftp = "https://www.python.org/ftp/python/{base_version}/"

    sources = [
        {
            "url": _pftp + "Python-{version}.tgz",
        }
    ]

    artifact_requirements = [
        "openssl (>=1.1.1)",
        "libb2 (>=0.98.1)",
        "uuid",
        "zlib",
    ]

    artifact_build_requirements = [
        "libb2-dev (>=0.98.1)",
        "libffi-dev (>=3.0.13)",
        "openssl-dev (>=1.1.1)",
        "uuid-dev",
        "zlib-dev",
    ]

    bundle_deps = [
        openssl.OpenSSL("3.1.5"),
        libb2.LibB2("0.98.1"),
        libffi.LibFFI("3.4.4"),
        libuuid.LibUUID("2.39.3"),
        zlib.Zlib("1.3.1"),
    ]

    @classmethod
    def get_source_url_variables(cls, version: str) -> dict[str, str]:
        base_ver = poetry_version.Version.parse(version).release.to_string()
        return {
            "base_version": base_ver,
        }

    def get_patches(self) -> dict[str, list[tuple[str, str]]]:
        v = f"{self.version.major}{self.version.minor}"

        patches = dict(super().get_patches())
        for pkg, pkg_patches in patches.items():
            if pkg == self.name:
                filtered = []
                for i, (pn, pfile) in enumerate(list(pkg_patches)):
                    m = re.match(r"^.*-(\d+)$", pn)
                    if m and m.group(1) != v:
                        pass
                    else:
                        filtered.append((pn, pfile))
                patches[pkg] = filtered
                break

        return patches

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")

        configure = sdir / "configure"

        configure_flags = {
            "--prefix": build.get_full_install_prefix(),
            "--sysconfdir": build.get_install_path("sysconf"),
            "--datarootdir": build.get_install_path("data"),
            "--bindir": build.get_install_path("bin"),
            "--libdir": build.get_install_path("lib"),
            "--includedir": build.get_install_path("include"),
            "--enable-ipv6": None,
            "--with-dbmliborder": "bdb:gdbm",
            "--with-computed-gotos": None,
        }

        if build.extra_optimizations_enabled():
            if build.supports_pgo():
                configure_flags["--enable-optimizations"] = None
            if build.supports_lto():
                configure_flags["--with-lto"] = None
            if build.uses_modern_gcc():
                build.sh_append_flags(
                    configure_flags,
                    "CFLAGS",
                    ("-fno-semantic-interposition",),
                )

        if "musl" in build.target.triple:
            # Set explicit stack size on musl where the default is too
            # low to support the default recursion limit.
            # See https://github.com/python/cpython/issues/76488
            build.sh_append_flags(
                configure_flags,
                "LDFLAGS",
                ("-Wl,-z,stack-size=1000000",),
            )

        if platform.system() == "Darwin":
            configure_flags["--enable-universalsdk"] = (
                "!$(xcrun --show-sdk-path)"
            )
            arch = build.target.machine_architecture
            if arch == "x86_64":
                configure_flags["--with-universal-archs"] = "intel-64"
            elif arch == "aarch64":
                configure_flags["--with-universal-archs"] = "arm-64"
            else:
                raise RuntimeError(f"unexpected architecture: {arch}")

        self.configure_dependency(build, configure_flags, "libffi", "LIBFFI")
        libffi_pkg = build.get_package("libffi")
        if not build.is_bundled(libffi_pkg):
            # This is somewhat confusing, but Python treats
            # --without-system-ffi on macOS as instruction to actually
            # _use_ the native system libffi (as opposed to pkg-config),
            # and ignores this option on other platforms.
            configure_flags["--without-system-ffi"] = None

        openssl_pkg = build.get_package("openssl")
        if build.is_bundled(openssl_pkg):
            openssl_path = build.get_install_dir(
                openssl_pkg, relative_to="pkgbuild"
            )
            openssl_path /= build.get_full_install_prefix().relative_to("/")
            configure_flags["--with-openssl"] = openssl_path
            configure_flags["--with-openssl-rpath"] = (
                openssl_pkg.get_shlib_paths(build)[0]
            )

        self.configure_dependency(build, configure_flags, "uuid", "LIBUUID")
        self.configure_dependency(build, configure_flags, "zlib", "ZLIB")
        self.configure_dependency(build, configure_flags, "libb2", "LIBB2")

        return build.sh_configure(configure, configure_flags)

    def get_make_env(self, build: targets.Build, wd: str) -> str:
        env = super().get_make_env(build, wd)
        openssl_pkg = build.get_package("openssl")
        libffi_pkg = build.get_package("libffi")
        libb2_pkg = build.get_package("libb2")
        uuid_pkg = build.get_package("uuid")
        zlib_pkg = build.get_package("zlib")
        ld_env = build.get_ld_env(
            [openssl_pkg, libffi_pkg, uuid_pkg, zlib_pkg, libb2_pkg], wd
        )
        return env + " ".join(ld_env)

    def get_build_script(self, build: targets.Build) -> str:
        make = build.sh_get_command("make")

        prefix = build.get_full_install_prefix().relative_to("/")
        dest = build.get_temp_root(relative_to="pkgbuild")

        if platform.system() == "Darwin":
            exe_suffix = ".exe"
        else:
            exe_suffix = ""

        sitescript = (
            f"import site; import pathlib; "
            f"print(pathlib.Path( "
            f'site.getsitepackages([\\"${{p}}\\"])[0]).resolve())'
        )

        python = f"python{exe_suffix}"

        wrapper_env = self.get_make_env(build, "${d}")
        bash = build.sh_get_command("bash")

        make_wrapper = textwrap.dedent(
            f"""\
            echo '#!{bash}' > python-wrapper
            echo set -Exe -o pipefail >> python-wrapper
            echo 'd=$(cd -- "$(dirname "$0")" >/dev/null 2>&1; pwd -P)' \\
                >> python-wrapper
            echo 'unset __PYVENV_LAUNCHER__' >> python-wrapper
            {f"echo 'export {wrapper_env}' >> python-wrapper"
             if wrapper_env else ""}
            echo 'p=${{d}}/{dest}/{prefix}' >> python-wrapper
            echo 's=$(${{d}}/{python} -c "{sitescript}")' >> python-wrapper
            echo export PYTHONPATH='${{s}}':"${{EXTRA_PYTHONPATH}}" \\
                >> python-wrapper
            echo exec '${{d}}/{python}' '"$@"' >> python-wrapper
            chmod +x python-wrapper
            cat python-wrapper
        """
        )

        disabled_modules = [
            "_sqlite3",
            "_tkinter",
            "_dbm",
            "_gdbm",
            "_lzma",
            "_bz2",
            "_curses",
            "_curses_panel",
            "_crypt",
            "audioop",
            "readline",
            "nis",
            "ossaudiodev",
            "spwd",
        ]

        make_env = self.get_make_env(build, "$(pwd)")

        return textwrap.dedent(
            f"""\
            # make sure no funny business is going on if metapkg
            # is ran from a venv.
            unset __PYVENV_LAUNCHER__
            echo '*disabled*' >> Modules/Setup.local
            echo '' >> Modules/Setup.local
            echo {' '.join(disabled_modules)} >> Modules/Setup.local
            # make sure config.c is regenerated reliably by make
            rm Modules/config.c
            ls -al Modules/
            {make} {make_env}
            ./{python} -m ensurepip --root "{dest}"
            {make_wrapper}"""
        )

    def get_make_install_env(self, build: targets.Build, wd: str) -> str:
        env = super().get_make_install_env(build, wd)
        return f"{env} ENSUREPIP=no"

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        installdest = build.get_install_dir(self, relative_to="pkgbuild")

        openssl_pkg = build.get_package("openssl")
        if build.is_bundled(openssl_pkg):
            # We must bundle the CA certificates if OpenSSL is bundled.
            python = build.sh_get_command("python", package=self)
            temp = build.get_temp_root(relative_to="pkgbuild")
            sslpath = (
                "import ssl; "
                "print(ssl.get_default_verify_paths().openssl_cafile)"
            )
            certifipath = "import certifi; " "print(certifi.where())"
            extra_install = textwrap.dedent(
                f"""\
                "{python}" -m pip install \\
                    --upgrade --force-reinstall \\
                    --root "{temp}" "certifi"
                sslpath=$("{python}" -c "{sslpath}")
                ssl_instpath="$(pwd)/{installdest}/${{sslpath}}"
                mkdir -p "$(dirname ${{ssl_instpath}})"
                certifipath=$("{python}" -c "{certifipath}")
                cp "${{certifipath}}" "${{ssl_instpath}}"
                """
            )
        else:
            extra_install = ""

        bin_dir = build.get_install_path("bin")
        minorv = self.version.minor
        extra_install += textwrap.dedent(
            f"""\
            rm $(pwd)/"{installdest}"/"{bin_dir}"/python3
            mv $(pwd)/"{installdest}"/"{bin_dir}"/python3.{minorv} \
                $(pwd)/"{installdest}"/"{bin_dir}"/python3
            """
        )

        script += textwrap.dedent(
            f"""\
            {extra_install}
            """
        )

        return script

    def get_install_list_script(self, build: targets.Build) -> str:
        script = super().get_install_list_script(build)
        openssl_pkg = build.get_package("openssl")
        python = build.sh_get_command("python", package=self)
        if build.is_bundled(openssl_pkg):
            sslpath = (
                "import ssl; "
                "print(ssl.get_default_verify_paths().openssl_cafile)"
            )
            script += f'\n"{python}" -c "{sslpath}"'

        return script

    def get_build_tools(self, build: targets.Build) -> dict[str, pathlib.Path]:
        build_dir = build.get_build_dir(self)
        return {"python": build_dir / "python-wrapper"}
