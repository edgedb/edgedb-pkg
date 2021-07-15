from __future__ import annotations
from typing import *

import pathlib
import platform
import re
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
        sdir = shlex.quote(
            str(build.get_source_dir(self, relative_to='pkgbuild')))
        copy_sources = f'test ./ -ef {sdir} || cp -a {sdir}/* ./'

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
            {make}
        ''')

    def get_build_install_script(self, build) -> str:
        installdest = build.get_install_dir(self, relative_to='pkgbuild')
        make = build.target.sh_get_command('make')

        return textwrap.dedent(f'''\
            {make} DESTDIR=$(pwd)/"{installdest}" install_sw
        ''')

    def get_shlib_paths(self, build) -> List[pathlib.Path]:
        return [build.get_full_install_prefix() / 'lib']

    def get_include_paths(self, build) -> List[pathlib.Path]:
        return [build.get_full_install_prefix() / 'include']

    @classmethod
    def from_upstream_version(cls, version: str) -> OpenSSL:
        pat = r"(?P<ver>(\d+)(\.(\d+))*)(?P<patchver>[a-z]?)"
        if m := re.match(pat, version):
            if m.group("patchver"):
                pep440_version = f"{m.group('ver')}.{ord(m.group('patchver'))}"
            else:
                pep440_version = m.group("ver")
        else:
            raise ValueError(
                f"OpenSSL version does not match expected pattern: {version}")

        return OpenSSL(pep440_version, source_version=version)
