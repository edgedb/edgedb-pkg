import textwrap

from poetry import packages as poetry_pkg

from metapkg import packages
from metapkg.packages import python

from edgedbpkg import postgresql, python as python_bundle, edgedbpy


python.set_python_runtime_dependency(poetry_pkg.Dependency(
    name='python-edgedb', constraint='3.7.*'
))


class EdgeDB(packages.BundledPythonPackage):

    title = "EdgeDB"
    name = 'edgedb'
    description = 'Next generation object-relational database'
    license = 'ASL 2.0'
    group = 'Applications/Databases'
    identifier = 'com.edgedb.edgedb'
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
        'postgresql-edgedb (== 11.1)',
        'pypkg-edgedb',
    ]

    bundle_deps = [
        postgresql.PostgreSQL(version='11.1'),
        python_bundle.Python(version='3.7.2'),
        edgedbpy.EdgeDBPython(version='0.0.1'),
    ]

    @property
    def slot(self) -> str:
        return str(self.version.major)

    def get_bdist_wheel_command(self, build) -> list:
        bindir = build.get_install_path('bin')
        runstate = build.get_install_path('runstate') / 'edgedb'
        pg_config = bindir / 'pg_config'
        return (
            ['build', f'--pg-config={pg_config}',
             f'--runstatedir={runstate}'] +
            super().get_bdist_wheel_command(build)
        )

    def get_build_script(self, build) -> str:
        script = super().get_build_script(build)
        pg_config = build.sh_get_command('pg_config')
        make = build.target.sh_get_command('make')
        srcdir = build.get_source_dir(self, relative_to='pkgbuild')

        script += textwrap.dedent(f'''\
            {make} -C "{srcdir}/ext" PG_CONFIG="$(pwd)/{pg_config}"
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
                PG_CONFIG="$(pwd)/{pg_config}" \\
                DESTDIR="$(pwd)/{dest}" \\
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
            shell=True, system=True,
            description='EdgeDB Server')

        return user_script

    def get_after_install_script(self, build) -> str:

        ensuredir = build.target.get_action('ensuredir', build)

        dataroot = build.get_install_path('localstate') / 'lib' / 'edgedb'
        dataroot_script = ensuredir.get_script(
            path=dataroot, owner_user='edgedb', owner_group='edgedb',
            owner_recursive=True)

        datadir = dataroot / str(self.version.major) / 'data'
        datadir_script = ensuredir.get_script(
            path=datadir, owner_user='edgedb', owner_group='edgedb',
            mode=0o700)

        ctl = build.get_install_path('bin') / 'edgedb-server'
        bootstrap_script = build.sh_format_command(
            ctl, {'-D': datadir, '--bootstrap': None})

        script = '\n'.join([datadir_script, dataroot_script])
        script += '\n' + build.get_su_script(bootstrap_script, user='edgedb')

        bindir = build.get_install_path('bin')
        pathfile = f'{dataroot}/current'
        script += '\n' + f'[ -e "{pathfile}" ] || echo {bindir} > "{pathfile}"'

        return script

    def get_exposed_commands(self, build) -> list:
        bindir = build.get_install_path('bin')

        return [
            bindir / 'edgedb',
        ]
