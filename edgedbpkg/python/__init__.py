from __future__ import annotations
from typing import *

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

    artifact_build_requirements = [
        'libffi-dev; extra == "capability-libffi"',
        'openssl-dev (>=1.0.2)',
        'zlib-dev',
    ]

    bundle_deps = [
        openssl.OpenSSL(version='1.1.1j')
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

        if build.extra_optimizations_enabled():
            if build.supports_pgo():
                configure_flags['--enable-optimizations'] = None
            if build.supports_lto():
                configure_flags['--with-lto'] = None

        if 'libffi' not in build.target.get_capabilities():
            configure_flags['--without-system-ffi'] = None

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

    def _get_make_env(self, build, wd: str) -> str:
        openssl_pkg = build.get_package('openssl')
        env = build.get_ld_env([openssl_pkg], wd)
        return ' '.join(env)

    def get_build_script(self, build) -> str:
        make = build.sh_get_command('make')

        prefix = build.get_full_install_prefix().relative_to('/')
        dest = build.get_temp_root(relative_to='pkgbuild')

        if platform.system() == 'Darwin':
            exe_suffix = '.exe'
        else:
            exe_suffix = ''

        sitescript = (
            f'import site; import pathlib; '
            f'print(pathlib.Path( '
            f'site.getsitepackages([\\"${{p}}\\"])[0]).resolve())'
        )

        python = f'python{exe_suffix}'

        wrapper_env = self._get_make_env(build, '${d}')
        bash = build.sh_get_command('bash')

        make_wrapper = textwrap.dedent(f'''\
            echo '#!{bash}' > python-wrapper
            echo 'd=$(dirname $0)' >> python-wrapper
            echo 'unset __PYVENV_LAUNCHER__' >> python-wrapper
            {f"echo 'export {wrapper_env}' >> python-wrapper"
             if wrapper_env else ""}
            echo 'p=${{d}}/{dest}/{prefix}' >> python-wrapper
            echo 's=$(${{d}}/{python} -c "{sitescript}")' >> python-wrapper
            echo export PYTHONPATH='${{s}}' >> python-wrapper
            echo exec '${{d}}/{python}' '"$@"' >> python-wrapper
            chmod +x python-wrapper
            cat python-wrapper
        ''')

        disabled_modules = '_sqlite3 _tkinter _dbm _gdbm _lzma _bz2'
        make_env = self._get_make_env(build, '$(pwd)')

        return textwrap.dedent(f'''\
            # make sure no funny business is going on if metapkg
            # is ran from a venv.
            unset __PYVENV_LAUNCHER__
            echo '*disabled*' >> Modules/Setup.local
            echo '' >> Modules/Setup.local
            echo {disabled_modules} >> Modules/Setup.local
            # make sure config.c is regenerated reliably by make
            rm Modules/config.c
            ls -al Modules/
            {make} {make_env}
            ./{python} -m ensurepip --root "{dest}"
            {make_wrapper}
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.sh_get_command('make')

        openssl_pkg = build.get_package('openssl')
        if build.is_bundled(openssl_pkg):
            # We must bundle the CA certificates if OpenSSL is bundled.
            python = build.sh_get_command('python', package=self)
            temp = build.get_temp_root(relative_to='pkgbuild')
            sslpath = (
                'import ssl; '
                'print(ssl.get_default_verify_paths().openssl_cafile)'
            )
            certifipath = (
                'import certifi; '
                'print(certifi.where())'
            )
            extra_install = textwrap.dedent(f'''\
                "{python}" -m pip install \\
                    --upgrade --force-reinstall \\
                    --root "{temp}" "certifi"
                sslpath=$("{python}" -c "{sslpath}")
                ssl_instpath="$(pwd)/{installdest}/${{sslpath}}"
                mkdir -p "$(dirname ${{ssl_instpath}})"
                certifipath=$("{python}" -c "{certifipath}")
                cp "${{certifipath}}" "${{ssl_instpath}}"
            ''')
        else:
            extra_install = ''

        env = self._get_make_env(build, '$(pwd)')

        return textwrap.dedent(f'''\
            {make} -j1 DESTDIR=$(pwd)/"{installdest}" {env} \
                ENSUREPIP=no install
            {extra_install}
        ''').strip()

    def get_install_list_script(self, build) -> str:
        script = super().get_install_list_script(build)
        openssl_pkg = build.get_package('openssl')
        python = build.sh_get_command('python', package=self)
        if build.is_bundled(openssl_pkg):
            sslpath = (
                'import ssl; '
                'print(ssl.get_default_verify_paths().openssl_cafile)'
            )
            script += f'\n"{python}" -c "{sslpath}"'

        return script

    def get_build_tools(self, build) -> dict:
        build_dir = build.get_build_dir(self)
        return {
            'python': f'{build_dir}/python-wrapper'
        }
