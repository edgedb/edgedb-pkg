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

    artifact_build_requirements = [
        'openssl (>=1.0.2)',
        'zlib',
    ]

    bundle_deps = [
        openssl.OpenSSL(version='1.0.2o')
    ]

    def get_configure_script(self, build) -> str:
        sdir = build.get_source_dir(self, relative_to='pkgbuild')

        configure = sdir / 'configure'

        return textwrap.dedent(f'''\
            {configure} \\
                --prefix={build.get_install_prefix()} \\
                --sysconfdir={build.get_install_path('sysconf')} \\
                --datarootdir={build.get_install_path('data')} \\
                --bindir={build.get_install_path('bin')} \\
                --libdir={build.get_install_path('lib')} \\
                --includedir={build.get_install_path('include')} \\
                --enable-ipv6 \\
                --with-dbmliborder=bdb:gdbm \\
                --with-computed-gotos
        ''')

    def get_build_script(self, build) -> str:
        make = build.sh_get_command('make')

        prefix = build.get_install_prefix().relative_to('/')
        dest = build.get_temp_root(relative_to='pkgbuild')

        sitescript = (
            f'import site; '
            f'print(site.getsitepackages([\\"${{p}}\\"])[0])'
        )

        make_wrapper = textwrap.dedent(f'''\
            echo '#!/bin/sh' > python-wrapper
            echo 'd=$(dirname $0)' >> python-wrapper
            echo 'p=${{d}}/{dest}/{prefix}' >> python-wrapper
            echo 's=$(${{d}}/python -c "{sitescript}")' >> python-wrapper
            echo export PYTHONPATH='${{s}}' >> python-wrapper
            echo exec '${{d}}/python' '"$@"' >> python-wrapper
            chmod +x python-wrapper
        ''')

        return textwrap.dedent(f'''\
            {make}
            ./python -m ensurepip --root "{dest}"
            {make_wrapper}
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} DESTDIR="{installdest}" ENSUREPIP=no install
        ''')

    def get_build_tools(self, build) -> dict:
        build_dir = build.get_build_dir(self)
        return {
            'python': f'{build_dir}/python-wrapper'
        }
