import pathlib
import platform
import textwrap

from metapkg import packages

from edgedbpkg import icu, openssl


class PostgreSQL(packages.BundledPackage):

    title = "PostgreSQL"
    name = 'postgresql-edgedb'

    sources = (
        {
            'url': 'git+https://github.com/postgres/postgres.git',
        },
    )

    artifact_requirements = [
        'icu (>=50)',
        'openssl (>=1.0.2)',
        'pam',
        'uuid',
        'zlib',
    ]

    artifact_build_requirements = [
        'bison',
        'flex',
        'perl',
        'systemd-dev ; extra == "capability-systemd"',
        'icu-dev (>=50)',
        'openssl-dev (>=1.0.2)',
        'pam-dev',
        'uuid-dev',
        'zlib-dev',
    ]

    bundle_deps = [
        openssl.OpenSSL(version='1.1.1j'),
        icu.ICU(version='68.2'),
    ]

    @classmethod
    def to_vcs_version(cls, version: str) -> str:
        return f"REL_{version.replace('.', '_')}"

    def get_configure_script(self, build) -> str:
        extra_version = ''

        system = platform.system()
        if system.endswith('BSD'):
            uuid_lib = 'bsd'
        elif system == 'Linux' or system == 'Darwin':
            # macOS actually ships the e2fs version despite being a "BSD"
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
            '--with-uuid': uuid_lib,
            '--without-readline': None,
        }

        icu_pkg = build.get_package('icu')
        if build.is_bundled(icu_pkg):
            icu_path = build.get_install_dir(
                icu_pkg, relative_to='pkgbuild')
            icu_path /= build.get_full_install_prefix().relative_to('/')
            icu_path = f'$(pwd)/"{icu_path}"'
            configure_flags['ICU_CFLAGS'] = f'!-I{icu_path}/include/'
            configure_flags['ICU_LIBS'] = (
                f'!-L{icu_path}/"lib -licui18n -licuuc -licudata"')

        openssl_pkg = build.get_package('openssl')
        if build.is_bundled(openssl_pkg):
            openssl_root = build.get_install_dir(
                openssl_pkg, relative_to='pkgbuild')
            openssl_path = (openssl_root
                            / build.get_full_install_prefix().relative_to('/'))
            openssl_path = f'$(pwd)/"{openssl_path}"'
            configure_flags['OPENSSL_CFLAGS'] = (
                f'!-I{openssl_path}/"include/ -L"{openssl_path}/lib')
            configure_flags['OPENSSL_LIBS'] = (
                f'!-L{openssl_path}/"lib -lssl -lcrypto"')
            configure_flags['LDFLAGS'] = f'!-L{openssl_path}/lib'

            if system == 'Darwin':
                # ./configure tries to compile and test a program
                # and it fails because openssl is not yet installed
                # at its install_name location.
                configure_flags['DYLD_FALLBACK_LIBRARY_PATH'] = openssl_root

        if build.target.has_capability('tzdata'):
            zoneinfo = build.target.get_resource_path(build, 'tzdata')
            configure_flags['--with-system-tzdata'] = zoneinfo

        if build.target.has_capability('systemd'):
            configure_flags['--with-systemd'] = None

        if build.extra_optimizations_enabled() and build.supports_lto():
            configure_flags['CFLAGS'] = (
                '-O2 -flto -fuse-linker-plugin '
                '-ffat-lto-objects -flto-partition=none'
            )

        return build.sh_format_command(
            configure, configure_flags, force_args_eq=True)

    def get_build_script(self, build) -> str:
        make = build.sh_get_command('make')

        wrapper_path = pathlib.Path('_install') / 'pg_config_wrapper'
        wrapper_cmd = build.sh_get_command(
            'pg_config_wrapper', relative_to='pkgbuild')

        bash = build.sh_get_command('bash')
        make_pg_config_wrapper = textwrap.dedent(f'''\
            echo '#!{bash}' >> "{wrapper_path}"
            echo 'set -ex' >> "{wrapper_path}"
            echo 'pushd "$(dirname $0)/../" >/dev/null' >> "{wrapper_path}"
            echo '{wrapper_cmd}' '"${{@}}"' >> "{wrapper_path}"
            echo 'popd >/dev/null' >> "{wrapper_path}"
            chmod +x "{wrapper_path}"
        ''')

        return textwrap.dedent(f'''\
            {make}
            {make} -C contrib
            {make} DESTDIR=$(pwd)/_install install
            {make} -C contrib DESTDIR=$(pwd)/_install install
            {make_pg_config_wrapper}
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.target.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} DESTDIR=$(pwd)/"{installdest}" install
            {make} DESTDIR=$(pwd)/"{installdest}" -C contrib install
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
