import platform
import textwrap
import shlex

from metapkg import packages


class OpenSSL(packages.BundledPackage):

    title = "OpenSSL"
    name = 'openssl'
    aliases = ['openssl-dev']

    _server = 'https://www.openssl.org/source/'

    sources = [
        {
            'url': _server + '/openssl-{version}.tar.gz',
            'csum_url': _server + '/openssl-{version}.tar.gz.sha256',
            'csum_algo': 'sha256',
        }
    ]

    def get_configure_script(self, build) -> str:
        sdir = build.get_source_dir(self, relative_to='pkgbuild')
        copy_sources = f'cp -a {shlex.quote(str(sdir))}/* ./'

        configure = './config'

        configure_flags = {
            '--prefix': build.get_full_install_prefix(),
            '--openssldir': build.get_full_install_prefix() / 'etc' / 'ssl',
            'no-ssl2': None,
            'no-ssl3': None,
            'shared': None,
            'enable-ec_nistp_64_gcc_128': None,
        }

        cfgcmd = build.sh_format_command(configure, configure_flags)
        if platform.system() == 'Darwin':
            # Force 64-bit build
            cfgcmd = f'KERNEL_BITS=64 {cfgcmd}'

        return '\n\n'.join([
            copy_sources,
            cfgcmd,
        ])

    def get_build_script(self, build) -> str:
        make = build.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} -j1
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.target.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} DESTDIR=$(pwd)/"{installdest}" -j1 install
        ''')
