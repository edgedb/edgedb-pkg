import datetime
import platform
import textwrap
import typing

from poetry import packages as poetry_pkg

from metapkg import packages
from metapkg.packages import python

from edgedbpkg import postgresql
from edgedbpkg import python as python_bundle


python.set_python_runtime_dependency(poetry_pkg.Dependency(
    name='python-edgedb', constraint='3.8.*'
))


class EdgeDB(packages.BundledPythonPackage):

    title = "EdgeDB"
    name = 'edgedb-server'
    description = 'Next generation object-relational database'
    license = 'ASL 2.0'
    group = 'Applications/Databases'
    identifier = 'com.edgedb.edgedb-server'
    url = 'https://edgedb.com/'

    sources = (
        {
            "url": "git+https://github.com/edgedb/edgedb.git",
            "extras": {
                # We obtain postgres from the fork repo directly,
                # so there's no need to clone it as a submodule.
                "exclude-submodules": ["postgres"],
                "clone-depth": 0,
            },
        },
    )

    artifact_requirements = [
        'postgresql-edgedb (== 12.3)',
        'pypkg-edgedb',
        'tzdata; extra == "capability-tzdata"',
    ]

    bundle_deps = [
        postgresql.PostgreSQL(version='12.3'),
        python_bundle.Python(version='3.8.3'),
    ]

    @property
    def slot(self) -> str:
        if self.version.prerelease:
            stage, no = self.version.prerelease
            return f'{self.version.major}-{stage}{no}'
        else:
            return f'{self.version.major}'

    def get_bdist_wheel_command(self, build) -> list:
        bindir = build.get_install_path('bin')
        runstate = build.get_install_path('runstate') / 'edgedb'
        shared_dir = build.get_install_path('data') / 'data'
        pg_config = bindir / 'pg_config'

        command = [
            'build',
            f'--pg-config={pg_config}',
            f'--runstatedir={runstate}',
            f'--shared-dir={shared_dir}',
        ]
        if 'dev' not in str(self.version):
            git_rev = self.resolve_version(build.io)
            curdate = datetime.datetime.now(tz=datetime.timezone.utc)
            curdate_str = curdate.strftime(r'%Y%m%d')
            command += [
                f'--version-suffix=g{git_rev[:9]}.d{curdate_str}'
            ]

        return command + super().get_bdist_wheel_command(build)

    def get_build_script(self, build) -> str:
        # Run edgedb-server --bootstrap to produce stdlib cache
        # for the benefit of faster bootstrap in the package.
        common_script = super().get_build_script(build)

        pg_pkg = build.get_package('postgresql-edgedb')
        icu_pkg = build.get_package('icu')
        openssl_pkg = build.get_package('openssl')

        build_python = build.sh_get_command('python')
        temp_dir = build.get_temp_dir(self, relative_to='pkgbuild')
        cachedir = temp_dir / '_datacache'
        pg_temp_install_path = build.get_build_dir(
            pg_pkg, relative_to='pkgbuild') / '_install'
        bindir = build.get_install_path('bin').relative_to('/')
        libdir = build.get_install_path('lib').relative_to('/')
        pg_config = pg_temp_install_path / bindir / 'pg_config'
        pg_libpath = pg_temp_install_path / libdir

        temp_install_dir = (
            build.get_temp_root(relative_to='pkgbuild') /
            build.get_full_install_prefix().relative_to('/')
        )
        sitescript = (
            f'import site; '
            f'print(site.getsitepackages(["{temp_install_dir}"])[0])'
        )
        runstatescript = (
            'import tempfile; '
            'print(tempfile.mkdtemp())'
        )
        abspath = (
            'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())'
        )

        ld_env = ' '.join(
            build.get_ld_env(
                deps=[icu_pkg, openssl_pkg],
                wd='${_wd}',
                extra=['${_ldlibpath}'],
            )
        )

        if platform.system() == 'Darwin':
            # Workaround SIP madness on macOS and allow popen() calls
            # in postgres to inherit DYLD_LIBRARY_PATH.
            extraenv = 'PGOVERRIDESTDSHELL=1'
        else:
            extraenv = ''

        data_cache_script = textwrap.dedent(f'''\
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
                    _EDGEDB_BUILDMETA_PG_CONFIG_PATH="${{_pg_config}}" \\
                    _EDGEDB_WRITE_DATA_CACHE_TO="${{_cachedir}}" \\
                    "${{_build_python}}" \\
                        -m edb.server.main \\
                        --data-dir="${{_tempdir}}" \\
                        --runstate-dir="${{_tempdir}}" \\
                        --bootstrap
                    rm -rf "${{_tempdir}}"
            )

            mkdir ./share/
            cp "${{_cachedir}}"/* ./share/
            pwd
            ls -al ./share/
        ''')

        return f'{common_script}\n{data_cache_script}'

    def get_build_install_script(self, build) -> str:
        script = super().get_build_install_script(build)
        srcdir = build.get_source_dir(self, relative_to='pkgbuild')
        dest = build.get_install_dir(self, relative_to='pkgbuild')

        datadir = build.get_install_path('data')
        script += textwrap.dedent(f'''\
            mkdir -p "{dest}/{datadir}"
            cp -a "{srcdir}/tests" "{dest}/{datadir}"
            mkdir -p "{dest}/{datadir}/data/"
            cp -a ./share/* "{dest}/{datadir}/data/"
            chmod 644 "{dest}/{datadir}/data/"*
        ''')

        return script

    def get_private_libraries(self, build) -> list:
        # Automatic dependency introspection points to libpq.so,
        # since some Postgres' client binaries require it.  We _do_
        # ship it, but don't declare it as a capability, hence the
        # need to ignore it here.
        return ['libpq.*']

    def get_extra_system_requirements(self, build) -> dict:
        rc_deps = []
        if build.target.has_capability('systemd'):
            rc_deps.append('systemd')

        return {
            'before-install': ['adduser'],
            'after-install': rc_deps
        }

    def get_before_install_script(self, build) -> str:

        dataroot = build.get_install_path('localstate') / 'lib' / 'edgedb'

        action = build.target.get_action('adduser', build)
        user_script = action.get_script(
            name='edgedb', group='edgedb', homedir=dataroot,
            shell=True, system=True,
            description='EdgeDB Server')

        return user_script

    def get_after_install_script(self, build) -> str:

        ensuredir = build.target.get_action('ensuredir', build)

        dataroot = build.get_install_path('localstate') / 'lib' / 'edgedb'
        dataroot_script = ensuredir.get_script(
            path=dataroot, owner_user='edgedb', owner_group='edgedb',
            owner_recursive=True)

        datadir = dataroot / self.slot / 'data'
        datadir_script = ensuredir.get_script(
            path=datadir, owner_user='edgedb', owner_group='edgedb',
            mode=0o700)

        ctl = build.get_install_path('bin') / 'edgedb-server'
        bootstrap_script = build.sh_format_command(
            ctl, {'-D': datadir, '--bootstrap': None})

        error = (
            f'Error: could not create default EdgeDB cluster. '
            f'Please create it manually with '
            f'"sudo -u edgedb {bootstrap_script}"'
        )

        bootstrap_script = (
            f'if [ -z "${{_EDGEDB_INSTALL_SKIP_BOOTSTRAP}}" ]; then '
            f'{bootstrap_script} || echo {error} >&2; fi'
        )

        script = '\n'.join([datadir_script, dataroot_script])
        script += '\n' + build.get_su_script(bootstrap_script, user='edgedb')

        bindir = build.get_install_path('bin')
        pathfile = f'{dataroot}/current'
        script += '\n' + f'[ -e "{pathfile}" ] || echo {bindir} > "{pathfile}"'

        return script

    def get_exposed_commands(self, build) -> list:
        bindir = build.get_install_path('bin')

        return [
            bindir / 'edgedb-server',
        ]

    def get_meta_packages(
        self,
        build,
        root_version: str,
    ) -> typing.List[packages.MetaPackage]:
        return [
            packages.MetaPackage(
                name=f'edgedb-{self.slot}',
                description=f'{self.description} (server and client tools)',
                dependencies={
                    f'edgedb-server-{self.slot}': f'= {root_version}',
                    'edgedb-cli': '',
                }
            )
        ]

    def get_conflict_packages(
        self,
        build,
        root_version: str,
    ) -> typing.List[packages.MetaPackage]:
        return ['edgedb-common']
