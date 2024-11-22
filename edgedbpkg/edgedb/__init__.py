from __future__ import annotations
from typing import (
    TYPE_CHECKING,
)

import base64
import os
import pathlib
import platform
import textwrap

from poetry.core.constraints import version as poetry_version
from poetry.core.packages import dependency as poetry_dep

from metapkg import packages
from metapkg import targets
from metapkg.packages import python

from edgedbpkg import postgresql
from edgedbpkg.pgext import pgvector
from edgedbpkg.pgext import edb_stat_statements
from edgedbpkg import python as python_bundle
from edgedbpkg import pyentrypoint
from edgedbpkg import libprotobuf_c

if TYPE_CHECKING:
    from cleo.io import io as cleo_io


python.set_python_runtime_dependency(
    poetry_dep.Dependency(
        name="python-edgedb",
        constraint=">=3.10.0,<3.13.0",
        allows_prereleases=True,
    )
)


class EdgeDB(packages.BundledPythonPackage):
    title = "EdgeDB"
    ident = "edgedb-server"
    description = "Next generation graph-relational database"
    license_id = "Apache-2.0"
    group = "Applications/Databases"
    identifier = "com.edgedb.edgedb-server"
    url = "https://edgedb.com/"

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb.git",
            "extras": {
                # We obtain postgres from the fork repo directly,
                # so there's no need to clone it as a submodule.
                "exclude_submodules": ["postgres"],
                "clone_depth": 0,
            },
        },
    ]

    artifact_requirements = {
        ">=2.0,<3.0.rc1": [
            "postgresql-edgedb (~= 14.0)",
            "python-edgedb (~= 3.10.0)",
        ],
        ">=3.0rc1,<4.0.dev1": [
            "postgresql-edgedb (~= 14.0)",
            "python-edgedb (~= 3.11.0)",
            "pgext-pgvector (~= 0.4.0)",
        ],
        ">=4.0.dev1,<5.0.dev1": [
            "postgresql-edgedb (~= 15.0)",
            "python-edgedb (~= 3.11.0)",
            "pgext-pgvector (~= 0.4.0)",
        ],
        ">=5.0.dev1,<6.0.dev8898": [
            "postgresql-edgedb (~= 16.0)",
            "python-edgedb (~= 3.12.0)",
            "pgext-pgvector (~= 0.6.0)",
        ],
        ">=6.0.dev8898,<6.0.dev9001": [
            "postgresql-edgedb (~= 17.0)",
            "python-edgedb (~= 3.12.0)",
            "pgext-pgvector (~= 0.7.0)",
        ],
        ">=6.0.dev9001": [
            "postgresql-edgedb (~= 17.0)",
            "python-edgedb (~= 3.12.0)",
            "pgext-pgvector (~= 0.7.0)",
            "pgext-edb-stat-statements",
        ],
    }

    artifact_build_requirements = {
        ">=2.0,<3.0.rc1": [
            "postgresql-edgedb (~= 14.0)",
            "python-edgedb (~= 3.10.0)",
            "pyentrypoint (>=1.0.0)",
            "pypkg-setuptools (<70.2.0)",
        ],
        ">=3.0rc1,<4.0.dev1": [
            "postgresql-edgedb (~= 14.0)",
            "python-edgedb (~= 3.11.0)",
            "pgext-pgvector (~= 0.4.0)",
            "pyentrypoint (>=1.0.0)",
            "pypkg-setuptools (<70.2.0)",
        ],
        ">=4.0.dev1,<5.0.dev1": [
            "postgresql-edgedb (~= 15.0)",
            "python-edgedb (~= 3.11.0)",
            "pgext-pgvector (~= 0.4.0)",
            "pyentrypoint (>=1.0.0)",
            "pypkg-setuptools (<70.2.0)",
        ],
        ">=5.0.dev1,<6.0.dev8898": [
            "postgresql-edgedb (~= 16.0)",
            "python-edgedb (~= 3.12.0)",
            "pgext-pgvector (~= 0.6.0)",
            "pyentrypoint (>=1.0.0)",
            "pypkg-setuptools (<70.2.0)",
        ],
        ">=6.0.dev8898": [
            "postgresql-edgedb (~= 17.0)",
            "python-edgedb (~= 3.12.0)",
            "pgext-pgvector (~= 0.7.0)",
            "pyentrypoint (>=1.0.0)",
            "pypkg-setuptools (<70.2.0)",
            "libprotobuf-c-dev (>=1.5.0)",  # for libpg_query
        ],
    }

    bundle_deps = [
        postgresql.PostgreSQL(version="14.11"),
        postgresql.PostgreSQL(version="15.6"),
        postgresql.PostgreSQL(version="16.4"),
        postgresql.PostgreSQL(version="17.0"),
        python_bundle.Python(version="3.10.11"),
        python_bundle.Python(version="3.11.8"),
        python_bundle.Python(version="3.12.2"),
        pyentrypoint.PyEntryPoint(version="1.0.0"),
        pgvector.PgVector("v0.4.2"),
        pgvector.PgVector("v0.6.0"),
        pgvector.PgVector("v0.7.4"),
        libprotobuf_c.LibProtoBufC("1.5.0"),
    ]

    def __init__(
        self, version: str | poetry_version.Version, *args, **kwargs
    ) -> None:
        edb_stat_statements.StatStatements(version=version)
        super().__init__(version, *args, **kwargs)

    @classmethod
    def get_vcs_source(
        cls, io: cleo_io.IO, ref: str | None = None
    ) -> packages.GitSource | None:
        if ref is not None:
            try:
                ver = poetry_version.Version.parse(ref)
            except ValueError:
                pass
            else:
                repo = cls.resolve_vcs_repo(io)
                if ver.dev is not None:
                    # Resolve major.minor-devN
                    commit_count = repo.run("rev-list", "--count", "HEAD")
                    offset = int(commit_count) - ver.dev.number
                    if offset >= 0:
                        rev = repo.run(
                            "rev-list",
                            f"--skip={offset}",
                            "--max-count=1",
                            "HEAD",
                        )
                        if rev:
                            return super().get_vcs_source(io, rev)

        return super().get_vcs_source(io, ref)

    @classmethod
    def resolve(
        cls,
        io: cleo_io.IO,
        *,
        name: packages.NormalizedName | None = None,
        version: str | None = None,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
        requires: list[poetry_dep.Dependency] | None = None,
    ) -> EdgeDB:
        os.environ["EDGEDB_BUILD_OFFICIAL"] = "yes"
        os.environ["EDGEDB_BUILD_TARGET"] = (
            base64.b32encode(target.triple.encode())
            .decode()
            .rstrip("=")
            .lower()
        )
        if revision:
            os.environ["EDGEDB_BUILD_DATE"] = revision

        prev: str | None

        try:
            prev = os.environ["EDGEDB_BUILD_IS_RELEASE"]
        except KeyError:
            prev = None

        os.environ["EDGEDB_BUILD_IS_RELEASE"] = "1" if is_release else ""
        os.environ["BUILD_EXT_MODE"] = "skip"

        try:
            return super().resolve(
                io,
                name=name,
                version=version,
                revision=revision,
                is_release=is_release,
                target=target,
                requires=requires,
            )
        finally:
            if prev is None:
                os.environ.pop("EDGEDB_BUILD_IS_RELEASE", None)
            else:
                os.environ["EDGEDB_BUILD_IS_RELEASE"] = prev

            os.environ.pop("BUILD_EXT_MODE", None)

    @classmethod
    def get_next_feature_version(
        cls,
        version: poetry_version.Version,
    ) -> poetry_version.Version:
        return version.next_major()

    @classmethod
    def canonicalize_version(
        cls,
        io: cleo_io.IO,
        version: poetry_version.Version,
        *,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
    ) -> poetry_version.Version:
        if version.local:
            if isinstance(version.local, tuple):
                local = version.local
            else:
                local = (version.local,)

            for part in local:
                if isinstance(part, str) and part.startswith("s"):
                    # new version format
                    build_signature = part[1:]
                    if version.is_devrelease():
                        new_ver = version.without_local().replace(
                            pre=None,
                            local=(build_signature,),
                        )
                    else:
                        new_ver = version.without_local().replace(
                            local=(build_signature,),
                        )

                    return new_ver

        return version

    @classmethod
    def get_package_repository(
        cls, target: targets.Target, io: cleo_io.IO
    ) -> python.PyPiRepository:
        repo = super().get_package_repository(target, io)
        repo.register_package_impl("cryptography", Cryptography)
        repo.register_package_impl("cffi", Cffi)
        repo.register_package_impl("jwcrypto", JWCrypto)
        repo.register_package_impl("edgedb", EdgeDBPython)
        repo.register_package_impl("maturin", Maturin)
        return repo

    @property
    def base_slot(self) -> str:
        if self.version.is_prerelease():
            pre = self.version.pre
            assert pre is not None
            pre_phase = packages.semver_pre_tag(self.version)
            return f"{self.version.major}-{pre_phase}{pre.number}"
        else:
            return f"{self.version.major}"

    @property
    def slot(self) -> str:
        if ".s" in self.pretty_version:
            # New version format
            if self.version.is_devrelease():
                dev = self.version.dev
                assert dev is not None
                return f"{self.version.major}-{dev.phase}{dev.number}"
            elif self.version.is_prerelease():
                pre = self.version.pre
                assert pre is not None
                pre_phase = packages.semver_pre_tag(self.version)
                return f"{self.version.major}-{pre_phase}{pre.number}"
            else:
                return f"{self.version.major}"
        else:
            if self.version.text.find(".dev") == -1:
                return self.base_slot
            else:
                return f"{self.base_slot}-dev{self.get_catalog_version()}"

    def version_includes_revision(self) -> bool:
        return ".s" in self.pretty_version

    def get_catalog_version(self) -> str:
        _, local = self.pretty_version.split("+", 1)
        for entry in local.split("."):
            if entry.startswith("cv"):
                return entry[2:]

        raise RuntimeError(
            f"no catalog version in EdgeDB version: {self.pretty_version}"
        )

    def get_version_metadata_fields(self) -> dict[str, str]:
        fields = dict(super().get_version_metadata_fields())
        fields["cv"] = "catalog_version"
        return fields

    def sh_get_build_wheel_env(
        self,
        build: targets.Build,
        *,
        site_packages: str,
        wd: str,
    ) -> packages.Args:
        env = dict(
            super().sh_get_build_wheel_env(
                build, site_packages=site_packages, wd=wd
            )
        )
        bindir = build.get_install_path(self, "bin").relative_to("/")
        if build.target.is_portable():
            runstate = ""
        else:
            runstate = str(build.get_install_path(self, "runstate") / "edgedb")
        shared_dir = (
            build.get_install_path(self, "data") / "data"
        ).relative_to("/")
        temp_root = build.get_temp_root(relative_to="pkgsource")
        src_python = build.sh_get_command(
            "python", package=self, relative_to="pkgsource"
        )
        rel_bindir_script = ";".join(
            (
                "import os.path",
                "rp = os.path.relpath",
                f"sp = rp('{site_packages}', start='{temp_root}')",
                f"print(rp('{bindir}', start=os.path.join(sp, 'edb')))",
            )
        )

        pg_config = f'!"$("{src_python}" -c "{rel_bindir_script}")"/pg_config'

        rel_datadir_script = ";".join(
            (
                "import os.path",
                "rp = os.path.relpath",
                f"sp = rp('{site_packages}', start='{temp_root}')",
                f"print(rp('{shared_dir}', start=os.path.join(sp, 'edb')))",
            )
        )

        data_dir = f'!"$("{src_python}" -c "{rel_datadir_script}")"'

        env["EDGEDB_BUILD_PACKAGE"] = "1"
        env["EDGEDB_BUILD_PG_CONFIG"] = pg_config
        env["EDGEDB_BUILD_RUNSTATEDIR"] = runstate
        env["EDGEDB_BUILD_SHARED_DIR"] = data_dir
        env["_EDGEDB_BUILDMETA_SHARED_DATA_DIR"] = str(
            build.get_build_dir(self, relative_to="pkgsource") / "share"
        )

        openssl_pkg = build.get_package("openssl")
        if build.is_bundled(openssl_pkg):
            build.sh_replace_quoted_paths(
                env,
                "OPENSSL_LIB_DIR",
                build.sh_must_get_bundled_pkg_lib_path(
                    openssl_pkg,
                    relative_to="pkgbuild",
                    wd=wd,
                ),
            )
            build.sh_replace_quoted_paths(
                env,
                "OPENSSL_INCLUDE_DIR",
                build.sh_must_get_bundled_pkg_include_path(
                    openssl_pkg,
                    relative_to="pkgbuild",
                    wd=wd,
                ),
            )

        return env

    def get_build_script(self, build: targets.Build) -> str:
        # Run edgedb-server --bootstrap to produce stdlib cache
        # for the benefit of faster bootstrap in the package.
        common_script = super().get_build_script(build)

        if build.channel == "stable" and not self.version.is_stable():
            raise AssertionError(
                f"cannot build non-stable edgedb-server=={self.version} "
                f"for the stable channel"
            )

        pg_pkg = build.get_package("postgresql-edgedb")

        build_python = build.sh_get_command("python")
        temp_dir = build.get_temp_dir(self, relative_to="pkgbuild")
        cachedir = temp_dir / "_datacache"
        pg_temp_install_path = (
            build.get_build_dir(pg_pkg, relative_to="pkgbuild") / "_install"
        )
        bindir = build.get_install_path(self, "bin").relative_to("/")
        libdir = build.get_install_path(self, "lib").relative_to("/")
        pg_config = pg_temp_install_path / bindir / "pg_config"
        pg_libpath = pg_temp_install_path / libdir

        temp_install_dir = build.get_temp_root(
            relative_to="pkgbuild"
        ) / build.get_rel_install_prefix(self)
        sitescript = (
            f"import site; "
            f'print(site.getsitepackages(["{temp_install_dir}"])[0])'
        )
        runstatescript = "import tempfile; print(tempfile.mkdtemp())"
        abspath = (
            "import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())"
        )

        all_build_deps = build.get_build_reqs(self, recursive=True)
        ld_env_args = build.get_ld_env(
            deps=all_build_deps,
            wd="${_wd}",
            extra=["${_ldlibpath}"],
        )

        ld_env = build.sh_format_args(
            ld_env_args,
            force_args_eq=True,
            linebreaks=False,
        )

        if platform.system() == "Darwin":
            # Workaround SIP madness on macOS and allow popen() calls
            # in postgres to inherit DYLD_LIBRARY_PATH.
            extraenv = "PGOVERRIDESTDSHELL=1"
        else:
            extraenv = ""

        data_cache_script = textwrap.dedent(
            f"""\
            mkdir -p "{cachedir}"
            _tempdir=$("{build_python}" -c '{runstatescript}')
            if [ "$(whoami)" = "root" ]; then
                chown nobody "{cachedir}"
                chown nobody "${{_tempdir}}"
                _sudo="sudo -u nobody"
            else
                _sudo=""
            fi
            _pythonpath=$("{build_python}" -c '{sitescript}')
            _pythonpath=$("{build_python}" -c '{abspath}' "${{_pythonpath}}")
            _cachedir=$("{build_python}" -c '{abspath}' "{cachedir}")
            _pg_config=$("{build_python}" -c '{abspath}' "{pg_config}")
            _ldlibpath=$("{build_python}" -c '{abspath}' "{pg_libpath}")
            _build_python=$("{build_python}" -c '{abspath}' "{build_python}")
            _wd=$("{build_python}" -c '{abspath}' "$(pwd)")

            (
                cd ../;
                ${{_sudo}} env \\
                    {ld_env} {extraenv} \\
                    PYTHONPATH="${{_pythonpath}}" \\
                    PG_DISABLE_PS_DISPLAY=1 \\
                    _EDGEDB_BUILDMETA_PG_CONFIG_PATH="${{_pg_config}}" \\
                    _EDGEDB_WRITE_DATA_CACHE_TO="${{_cachedir}}" \\
                    "${{_build_python}}" \\
                        -m edb.server.main \\
                        --data-dir="${{_tempdir}}" \\
                        --runstate-dir="${{_tempdir}}" \\
                        --bootstrap-only
                    rm -rf "${{_tempdir}}"
            )

            mkdir -p ./share/
            cp "${{_cachedir}}"/* ./share/
            pwd
            ls -al ./share/
        """
        )

        return f"{common_script}\n{data_cache_script}"

    def get_extra_python_build_commands(
        self,
        build: targets.Build,
    ) -> list[str]:
        ver = (self.version.major, self.version.minor)
        if ver < (2, 0) or ver >= (2, 2):
            # 2.2+ builds the UI in `setup.py build`.
            return []

        src_python = build.sh_get_command(
            "python", package=self, relative_to="pkgsource"
        )
        share_dir = (
            build.get_build_dir(self, relative_to="pkgsource") / "share"
        )
        return [
            f'mkdir -p "{share_dir}"',
            f'env _EDGEDB_BUILDMETA_SHARED_DATA_DIR="{share_dir}" \\\n'
            f'  "{src_python}" setup.py build_ui',
        ]

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        srcdir = build.get_source_dir(self, relative_to="pkgbuild")
        dest = build.get_build_install_dir(self, relative_to="pkgbuild")

        datadir = build.get_install_path(self, "data")
        script += textwrap.dedent(
            f"""\
            mkdir -p "{dest}/{datadir}"
            cp -a "{srcdir}/tests" "{dest}/{datadir}"
            mkdir -p "{dest}/{datadir}/data/"
            cp -a ./share/* "{dest}/{datadir}/data/"
            chmod -R u+w,g+r,o+r "{dest}/{datadir}/data/"*
            """
        )

        bindir = build.get_install_path(self, "bin").relative_to("/")

        ep_helper_pkg = build.get_package("pyentrypoint")
        ep_helper = (
            build.get_temp_dir(ep_helper_pkg, relative_to="pkgbuild")
            / "bin"
            / "pyentrypoint"
        )

        script += textwrap.dedent(
            f"""\
            for p in "{dest}/{bindir}"/*; do
                if [ -f "$p" ]; then
                    mv "$p" "${{p}}.py"
                    chmod -x "${{p}}.py"
                    sed -i -e "/#!/d" "${{p}}.py"
                    cp "{ep_helper}" "$p"
                fi
            done
            """
        )

        return script

    def get_private_libraries(self, build: targets.Build) -> list[str]:
        # Automatic dependency introspection points to libpq.so,
        # since some Postgres' client binaries require it.  We _do_
        # ship it, but don't declare it as a capability, hence the
        # need to ignore it here.  Same applies to OpenSSL.
        return ["libpq.*", "libcrypto.*", "libssl.*"]

    def get_extra_system_requirements(
        self, build: targets.Build
    ) -> dict[str, list[str]]:
        rc_deps = []
        if build.target.has_capability("systemd"):
            rc_deps.append("systemd")

        return {"before-install": ["adduser"], "after-install": rc_deps}

    def get_before_install_script(self, build: targets.Build) -> str:
        dataroot = (
            build.get_install_path(self, "localstate") / "lib" / "edgedb"
        )

        action = build.target.get_action("adduser", build)
        assert isinstance(action, targets.AddUserAction)
        user_script = action.get_script(
            name="edgedb",
            group="edgedb",
            homedir=str(dataroot),
            shell=True,
            system=True,
            description="EdgeDB Server",
        )

        return user_script

    def get_exposed_commands(self, build: targets.Build) -> list[pathlib.Path]:
        bindir = build.get_install_path(self, "bin")

        return [
            bindir / "edgedb-server",
        ]

    def get_meta_packages(
        self,
        build: targets.Build,
        root_version: str,
    ) -> list[packages.MetaPackage]:
        return [
            packages.MetaPackage(
                name=f"edgedb-{self.slot}",
                description=f"{self.description} (server and client tools)",
                dependencies={
                    f"edgedb-server-{self.slot}": f"= {root_version}",
                    "edgedb-cli": "",
                },
            )
        ]

    def get_conflict_packages(
        self,
        build: targets.Build,
        root_version: str,
    ) -> list[str]:
        return ["edgedb-common"]

    def _get_edgedb_catalog_version(self, build: targets.Build) -> str:
        source = pathlib.Path(build.get_source_dir(self, relative_to="fsroot"))

        defines = source / "edb" / "buildmeta.py"
        if not defines.exists():
            defines = source / "edb" / "server" / "defines.py"

        with open(defines, "r") as f:
            for line in f:
                if line.startswith("EDGEDB_CATALOG_VERSION = "):
                    return str(int(line[len("EDGEDB_CATALOG_VERSION = ") :]))
            else:
                raise RuntimeError("cannot determine EDGEDB_CATALOG_VERSION")

    def get_provided_packages(
        self,
        build: targets.Build,
        root_version: str,
    ) -> list[tuple[str, str]]:
        catver = self._get_edgedb_catalog_version(build)
        return [("edgedb-server-catalog", catver)]


class Cryptography(packages.PythonPackage):
    def sh_get_build_wheel_env(
        self, build: targets.Build, *, site_packages: str, wd: str
    ) -> packages.Args:
        env = super().sh_get_build_wheel_env(
            build, site_packages=site_packages, wd=wd
        ) | {
            "OPENSSL_STATIC": "0",
        }

        openssl_pkg = build.get_package("openssl")
        if build.is_bundled(openssl_pkg):
            build.sh_replace_quoted_paths(
                env,
                "OPENSSL_LIB_DIR",
                build.sh_must_get_bundled_pkg_lib_path(
                    openssl_pkg,
                    relative_to="pkgbuild",
                    wd=wd,
                ),
            )
            build.sh_replace_quoted_paths(
                env,
                "OPENSSL_INCLUDE_DIR",
                build.sh_must_get_bundled_pkg_include_path(
                    openssl_pkg,
                    relative_to="pkgbuild",
                    wd=wd,
                ),
            )

        return env

    def get_requirements(self) -> list[poetry_dep.Dependency]:
        reqs = super().get_requirements()
        reqs.append(poetry_dep.Dependency("openssl", ">=1.1.1.100"))
        return reqs

    def get_build_requirements(self) -> list[poetry_dep.Dependency]:
        reqs = super().get_requirements()
        reqs.append(poetry_dep.Dependency("openssl-dev", ">=1.1.1.100"))
        return reqs


class Cffi(packages.PythonPackage):
    def get_requirements(self) -> list[poetry_dep.Dependency]:
        reqs = super().get_requirements()
        reqs.append(poetry_dep.Dependency("libffi", "*"))
        return reqs

    def get_build_requirements(self) -> list[poetry_dep.Dependency]:
        reqs = super().get_requirements()
        reqs.append(poetry_dep.Dependency("libffi", "*"))
        return reqs


class JWCrypto(packages.PythonPackage):
    def get_file_no_install_entries(self, build: targets.Build) -> list[str]:
        entries = super().get_file_no_install_entries(build)
        entries.append("{docdir}/jwcrypto")
        entries.append("{docdir}/jwcrypto/**")
        return entries


class EdgeDBPython(packages.PythonPackage):
    def get_file_no_install_entries(self, build: targets.Build) -> list[str]:
        entries = super().get_file_no_install_entries(build)
        entries.append("{bindir}/*")
        return entries


class Maturin(packages.PythonPackage):
    @property
    def provides_build_tools(self) -> bool:
        return True
