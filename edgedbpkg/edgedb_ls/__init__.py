from __future__ import annotations
from typing import TYPE_CHECKING

import base64
import os
import pathlib
import shlex
import textwrap

from poetry.core.packages import dependency as poetry_dep

from metapkg import packages
from metapkg import targets
from metapkg.packages import python

from edgedbpkg import python as python_bundle
from edgedbpkg import pyentrypoint
from edgedbpkg import edgedb as edgedb_server

if TYPE_CHECKING:
    from cleo.io import io as cleo_io
    from poetry.core.semver import version as poetry_version


python.set_python_runtime_dependency(
    poetry_dep.Dependency(
        name="python-edgedb",
        constraint=">=3.10.0,<3.13.0",
        allows_prereleases=True,
    )
)


class EdgeDBLanguageServer(packages.BundledPythonPackage):
    title = "EdgeDBLanguageServer"
    name = packages.canonicalize_name("edgedb-ls")
    description = "Language server for EdgeDB"
    license_id = "Apache-2.0"
    group = "Applications/Databases"
    identifier = "com.edgedb.edgedb-ls"
    url = "https://edgedb.com/"

    sources = [
        {
            "url": "git+https://github.com/edgedb/edgedb.git",
            "extras": {
                "exclude_submodules": [
                    # We obtain postgres from the fork repo directly,
                    # so there's no need to clone it as a submodule.
                    "postgres",

                    # TODO: make edgedb-server repo not build pgproto
                    # "edb/server/pgproto",

                    # TODO: make edgedb-server repo not build libpg_query
                    # "edb/pgsql/parser/libpg_query",
                ],
                "clone_depth": 0,
            },
        },
    ]

    artifact_requirements = {
        ">=5.0.dev1": [
            "python-edgedb (~= 3.12.0)",
        ],
    }

    artifact_build_requirements = [
        "pyentrypoint (>=1.0.0)",
    ]

    bundle_deps = [
        python_bundle.Python(version="3.10.11"),
        python_bundle.Python(version="3.11.8"),
        python_bundle.Python(version="3.12.2"),
        pyentrypoint.PyEntryPoint(version="1.0.0"),
    ]

    @classmethod
    def resolve(
        cls,
        io: cleo_io.IO,
        *,
        version: str | None = None,
        revision: str | None = None,
        is_release: bool = False,
        target: targets.Target,
    ) -> EdgeDBLanguageServer:
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
            return (
                super()
                .resolve(
                    io,
                    version=version,
                    revision=revision,
                    is_release=is_release,
                    target=target,
                )
                .with_features(["language-server"])
            )
        finally:
            if prev is None:
                os.environ.pop("EDGEDB_BUILD_IS_RELEASE", None)
            else:
                os.environ["EDGEDB_BUILD_IS_RELEASE"] = prev

            os.environ.pop("BUILD_EXT_MODE", None)

    def parse_version_metadata(
        self,
        segments: tuple[str | int, ...],
    ) -> dict[str, str]:
        return {}

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
        repo.register_package_impl("cryptography", edgedb_server.Cryptography)
        repo.register_package_impl("cffi", edgedb_server.Cffi)
        repo.register_package_impl("jwcrypto", edgedb_server.JWCrypto)
        repo.register_package_impl("edgedb", edgedb_server.EdgeDBPython)
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
                return f"{self.base_slot}-dev"

    def version_includes_revision(self) -> bool:
        return True

    def sh_get_build_wheel_env(
        self, build: targets.Build, *, site_packages_var: str
    ) -> dict[str, str]:
        env = dict(
            super().sh_get_build_wheel_env(
                build, site_packages_var=site_packages_var
            )
        )
        if build.target.is_portable():
            runstate = ""
        else:
            runstate = str(build.get_install_path("runstate") / "edgedb")

        env["EDGEDB_BUILD_PACKAGE"] = "1"
        env["EDGEDB_BUILD_RUNSTATEDIR"] = runstate
        return env

    def get_build_script(self, build: targets.Build) -> str:
        common_script = super().get_build_script(build)

        if build.channel == "stable" and not self.version.is_stable():
            raise AssertionError(
                f"cannot build non-stable edgedb-ls=={self.version} "
                f"for the stable channel"
            )

        return common_script

    def get_build_install_script(self, build: targets.Build) -> str:
        script = super().get_build_install_script(build)
        dest = build.get_install_dir(self, relative_to="pkgbuild")

        bindir = build.get_install_path("bin").relative_to("/")

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
        return ["libcrypto.*", "libssl.*"]

    def get_exposed_commands(self, build: targets.Build) -> list[pathlib.Path]:
        bindir = build.get_install_path("bin")

        return [
            bindir / "edgedb-ls",
        ]

    def get_conflict_packages(
        self,
        build: targets.Build,
        root_version: str,
    ) -> list[str]:
        return ["edgedb-common"]
