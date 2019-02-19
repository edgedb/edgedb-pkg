import platform
import textwrap

from metapkg import packages

from edgedbpkg import openssl


class Python(packages.BundledPackage):

    title = "Python"
    name = 'python-edgedb'

    _pftp = "https://www.python.org/ftp/python/{version}/"

    sources = [
        {
            'url': _pftp + 'Python-{version}.tgz',
            'pgpsig': _pftp + 'Python-{version}.tgz.asc',
        }
    ]

    artifact_requirements = [
        'openssl (>=1.0.2)',
        'zlib',
    ]

    bundle_deps = [
        openssl.OpenSSL(version='1.0.2o')
    ]

    def get_configure_script(self, build) -> str:
        sdir = build.get_source_dir(self, relative_to='pkgbuild')

        configure = sdir / 'configure'

        configure_flags = {
            '--prefix': build.get_full_install_prefix(),
            '--sysconfdir': build.get_install_path('sysconf'),
            '--datarootdir': build.get_install_path('data'),
            '--bindir': build.get_install_path('bin'),
            '--libdir': build.get_install_path('lib'),
            '--includedir': build.get_install_path('include'),
            '--enable-ipv6': None,
            '--with-dbmliborder': 'bdb:gdbm',
            '--with-computed-gotos': None,
        }

        if platform.system() == 'Darwin':
            configure_flags['--enable-universalsdk'] = (
                '!$(xcrun --show-sdk-path)')
            configure_flags['--with-universal-archs'] = 'intel-64'

        openssl_pkg = build.get_package('openssl')
        if build.is_bundled(openssl_pkg):
            openssl_path = build.get_install_dir(
                openssl_pkg, relative_to='pkgbuild')
            openssl_path /= build.get_full_install_prefix().relative_to('/')
            configure_flags['--with-openssl'] = openssl_path

        return build.sh_format_command(configure, configure_flags)

    def get_build_script(self, build) -> str:
        make = build.sh_get_command('make')

        prefix = build.get_full_install_prefix().relative_to('/')
        dest = build.get_temp_root(relative_to='pkgbuild')

        exe_suffix = ''
        sitescript = (
            f'import site; '
            f'print(site.getsitepackages([\\"${{p}}\\"])[0])'
        )

        openssl_pkg = build.get_package('openssl')
        if build.is_bundled(openssl_pkg):
            # Make sure bundled libssl gets found, since it's only a
            # temp install at this point.
            openssl_path = build.get_install_dir(
                openssl_pkg, relative_to='pkgbuild')
            openssl_lib_path = (
                openssl_path
                / build.get_install_path('lib').relative_to('/')
            )

            if platform.system() == 'Darwin':
                env = f'export DYLD_LIBRARY_PATH=$(pwd)/"{openssl_lib_path}"'
                exe_suffix = '.exe'
            else:
                env = f'export LD_LIBRARY_PATH=$(pwd)/"{openssl_lib_path}"'
        else:
            env = ''

        python = f'python{exe_suffix}'

        make_wrapper = textwrap.dedent(f'''\
            echo '#!/bin/sh' > python-wrapper
            echo 'unset __PYVENV_LAUNCHER__' >> python-wrapper
            echo {env} >> python-wrapper
            echo 'd=$(dirname $0)' >> python-wrapper
            echo 'p=${{d}}/{dest}/{prefix}' >> python-wrapper
            echo 's=$(${{d}}/{python} -c "{sitescript}")' >> python-wrapper
            echo export PYTHONPATH='${{s}}' >> python-wrapper
            echo exec '${{d}}/{python}' '"$@"' >> python-wrapper
            chmod +x python-wrapper
        ''')

        disabled_modules = '_sqlite3 _tkinter _dbm _gdbm _lzma _bz2'

        return textwrap.dedent(f'''\
            # make sure no funny business is going on if metapkg
            # is ran from a venv.
            unset __PYVENV_LAUNCHER__
            echo '*disabled*' >> Modules/Setup.local
            echo '' >> Modules/Setup.local
            echo {disabled_modules} >> Modules/Setup.local
            {env}
            {make}
            ./{python} -m ensurepip --root "{dest}"
            {make_wrapper}
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} DESTDIR=$(pwd)/"{installdest}" ENSUREPIP=no install
        ''')

    def get_build_tools(self, build) -> dict:
        build_dir = build.get_build_dir(self)
        return {
            'python': f'{build_dir}/python-wrapper'
        }
