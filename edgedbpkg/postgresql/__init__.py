import pathlib
import platform
import textwrap

from metapkg import packages

from edgedbpkg import openssl


class PostgreSQL(packages.BundledPackage):

    title = "PostgreSQL"
    name = 'postgresql-edgedb'

    sources = (
        {
            'url': 'git+https://github.com/edgedb/postgres.git',
            'extras': {
                'branch': 'edge_11',
            },
        },
    )

    artifact_build_requirements = [
        'bison',
        'flex',
        'icu',
        'libxml2',
        'libxslt',
        'openssl (>=1.0.2)',
        'pam',
        'uuid',
        'zlib',
        'systemd-dev ; extra == "capability-systemd"',
    ]

    bundle_deps = [
        openssl.OpenSSL(version='1.0.2o')
    ]

    def get_configure_script(self, build) -> str:
        extra_version = ''

        system = platform.system()
        if system.endswith('BSD') or system == 'Darwin':
            uuid_lib = 'bsd'
        elif system == 'Linux':
            uuid_lib = 'e2fs'
        else:
            raise NotImplementedError(
                f'unsupported target system: {system}')

        sdir = build.get_source_dir(self, relative_to='pkgbuild')
        configure = sdir / 'configure'

        configure_flags = {
            '--sysconfdir': build.get_install_path('sysconf'),
            '--datarootdir': build.get_install_path('data'),
            '--bindir': build.get_install_path('bin'),
            '--libdir': build.get_install_path('lib'),
            '--includedir': build.get_install_path('include'),
            '--with-extra-version': extra_version,
            '--with-icu': None,
            '--with-pam': None,
            '--with-openssl': None,
            '--with-libxml': None,
            '--with-libxslt': None,
            '--with-uuid': uuid_lib,
        }

        zoneinfo = build.target.get_resource_path(build, 'zoneinfo')
        if zoneinfo:
            configure_flags['--with-system-tzdata'] = zoneinfo

        if build.target.has_capability('systemd'):
            configure_flags['--with-systemd'] = None

        return build.sh_format_command(configure, configure_flags)

    def get_build_script(self, build) -> str:
        make = build.sh_get_command('make')

        wrapper_path = pathlib.Path('_install') / 'pg_config_wrapper'
        wrapper_cmd = build.sh_get_command(
            'pg_config_wrapper', relative_to='pkgbuild')

        make_pg_config_wrapper = textwrap.dedent(f'''\
            echo '#!/bin/bash' >> "{wrapper_path}"
            echo 'set -ex' >> "{wrapper_path}"
            echo 'pushd "$(dirname $0)/../" >/dev/null' >> "{wrapper_path}"
            echo '{wrapper_cmd}' '"${{@}}"' >> "{wrapper_path}"
            echo 'popd >/dev/null' >> "{wrapper_path}"
            chmod +x "{wrapper_path}"
        ''')

        return textwrap.dedent(f'''\
            {make}
            {make} -C contrib
            {make} DESTDIR="$(realpath _install)" install
            {make_pg_config_wrapper}
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.target.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} DESTDIR="$(realpath '{installdest}')" install
            {make} DESTDIR="$(realpath '{installdest}')" -C contrib install
        ''')

    def get_build_tools(self, build) -> dict:
        bindir = build.get_install_path('bin').relative_to('/')
        datadir = build.get_install_path('data')
        libdir = build.get_install_path('lib')
        temp_install_path = build.get_build_dir(self) / '_install'

        # Since we are using a temporary Postgres installation,
        # pg_config will return paths together with the temporary
        # installation prefix, so we need to wrap it to strip
        # it from certain paths.
        wrapper = textwrap.dedent(f'''\
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
        ''')

        wrapper_cmd = build.write_helper('pg_config_wrapper.py', wrapper,
                                         relative_to='sourceroot')

        return {
            'pg_config_wrapper': wrapper_cmd,
            'pg_config': temp_install_path / 'pg_config_wrapper'
        }
