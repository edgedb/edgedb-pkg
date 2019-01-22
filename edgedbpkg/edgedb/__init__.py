import textwrap

from poetry import packages as poetry_pkg

from metapkg import packages
from metapkg.packages import python

from edgedbpkg import postgresql, python as python_bundle


python.set_python_runtime_dependency(poetry_pkg.Dependency(
    name='python-edgedb', constraint='3.7.*'
))


class EdgeDB(packages.BundledPythonPackage):

    title = "EdgeDB Alpha"
    name = 'edgedb-server'
    slot = 'alpha'
    description = 'Next generation object-relational database'
    license = 'ASL 2.0'
    group = 'Applications/Databases'
    url = 'https://edgedb.com/'

    sources = (
        "git+https://github.com/edgedb/edgedb.git",
    )

    artifact_requirements = [
        'postgresql-edgedb (== 11.1)',
    ]

    bundle_deps = [
        postgresql.PostgreSQL(version='11.1'),
        python_bundle.Python(version='3.7.2'),
    ]

    def get_bdist_wheel_command(self, build) -> list:
        bindir = build.get_install_path('bin')
        pg_config = bindir / 'pg_config'
        return (
            ['build', f'--pg-config={pg_config}'] +
            super().get_bdist_wheel_command(build)
        )

    def get_build_script(self, build) -> str:
        script = super().get_build_script(build)
        pg_config = build.sh_get_command('pg_config')
        make = build.target.sh_get_command('make')
        srcdir = build.get_source_dir(self, relative_to='pkgbuild')

        script += textwrap.dedent(f'''\
            {make} -C "{srcdir}/ext" PG_CONFIG="$(realpath {pg_config})"
        ''')

        return script

    def get_build_install_script(self, build) -> str:
        script = super().get_build_install_script(build)
        pg_config = build.sh_get_command('pg_config')
        make = build.target.sh_get_command('make')
        srcdir = build.get_source_dir(self, relative_to='pkgbuild')
        dest = build.get_install_dir(self, relative_to='pkgbuild')

        script += textwrap.dedent(f'''\
            {make} -C "{srcdir}/ext" \\
                PG_CONFIG="$(realpath {pg_config})" \\
                DESTDIR="$(realpath {dest})" \\
                install
        ''')

        datadir = build.get_install_path('data')
        script += textwrap.dedent(f'''\
            cp -a "{srcdir}/tests" "{dest}/{datadir}"
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
            shell=True, system=True, description='EdgeDB Server')

        return user_script

    def get_after_install_script(self, build) -> str:

        script = ''

        dataroot = build.get_install_path('localstate') / 'lib' / 'edgedb'
        datadir = dataroot / str(self.version.major) / 'data'

        ctl = build.get_install_path('bin') / 'edgedb-server'
        bootstrap_script = build.sh_format_command(
            ctl, {'-D': datadir, '--bootstrap': None})

        script += build.get_su_script(bootstrap_script, user='edgedb')

        return script

    def get_exposed_commands(self, build) -> list:
        bindir = build.get_install_path('bin')

        return [
            bindir / 'edgedb-server',
            bindir / 'edgedb'
        ]
