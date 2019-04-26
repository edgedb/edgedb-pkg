##
# Copyright (c) 2017-present MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import base64
import pathlib
import textwrap

from edbsre import resources
from edbsre.lib import services
from edbsre.envs import edgedb1_prod
from edbsre.platform import gcp as gcp_platform
from edbsre.platform import k8s as k8s_platform


class PubPackagesService(services.Service):

    name = 'pub-packages'
    description = 'Service for EdgeDB release packages'
    hostname = 'packages.edgedb.com'

    @classmethod
    def get_instance_class(cls):
        return PubPackagesServiceInstance

    @classmethod
    def get_environments(cls):
        return [edgedb1_prod.EdgeDB1ProdEnv()]


class PubPackagesServiceInstance(services.ServiceInstance):

    def __init__(self, service, env):
        super().__init__(service, env)

        self.hostname = service.hostname.format(env=env.tag)

        defs = pathlib.Path(__file__).parent / 'defs'

        self.add_required_resource(
            resources.StaticIP(
                name=self.name,
            )
        )

        self.add_required_resource(
            resources.DNSName(
                name=self.name,
                ip_address_name=self.name,
                dns_name=self.hostname,
            )
        )

        self.add_required_resource(
            resources.StaticIP(
                name=f'{self.name}-upload',
                region=env.region,
            )
        )

        self.add_required_resource(
            resources.DNSName(
                name=f'{self.name}-upload',
                ip_address_name=f'{self.name}-upload',
                region=env.region,
                dns_name=f'upload-{self.hostname}',
            )
        )

        k8s_hostkeys = {}
        host_keys = env.platform.list_secrets('^edgedb-pkgserver-host-key.*')
        for host_key in host_keys:
            host_key_data = env.platform.get_secret(
                host_key,
                keyname='storage-host-auth',
            )
            _, _, kt = host_key.rpartition('-')
            keyname = f'ssh_host_{kt}_key'
            k8s_hostkeys[keyname] = base64.b64encode(host_key_data).decode()

        if k8s_hostkeys:
            self.add_required_resource(
                k8s_platform.K8SResource(
                    name=f'{self.name}-ssh-host-keys',
                    definition=textwrap.dedent(f'''\
                        apiVersion: v1
                        type: Opaque
                        kind: Secret
                        data:
                            {{data}}
                        metadata:
                            name: {self.name}-ssh-host-keys
                    ''').format(
                        data=textwrap.indent(
                            '\n'.join(f'{k}: {v}'
                                      for k, v in k8s_hostkeys.items()),
                            '    ').strip(),
                    ),
                ),
            )

        keys = {'root': 'authorized_keys', 'uploader': 'uploaders'}
        for user, fn in keys.items():
            ssh_ids = env.platform.get_ssh_ids(user, self.name)
            if not ssh_ids:
                continue

            data = base64.b64encode(ssh_ids.encode()).decode()

            self.add_required_resource(
                k8s_platform.K8SResource(
                    name=f'{self.name}-ssh-{user}-authorized-keys',
                    definition=textwrap.dedent(f'''\
                        apiVersion: v1
                        type: Opaque
                        kind: Secret
                        data:
                            {fn}: {data}
                        metadata:
                            name: {self.name}-ssh-{user}-authorized-keys
                    ''')
                ),
            )

        signing_key = env.platform.get_secret(
            'edgedb-release-signing-key',
            keyname='gpg-keys-high')

        signing_keydata = base64.b64encode(signing_key).decode()

        self.add_required_resource(
            k8s_platform.K8SResource(
                name=f'{self.name}-gpg-keys',
                definition=textwrap.dedent(f'''\
                    apiVersion: v1
                    type: Opaque
                    kind: Secret
                    data:
                        edgedb-signing.asc: {signing_keydata}
                    metadata:
                        name: {self.name}-gpg-keys
                ''')
            )
        )

        signing_public_key = env.platform.get_secret(
            'edgedb-release-signing-public-key',
            keyname='gpg-keys-high')

        signing_public_keydata = base64.b64encode(signing_public_key).decode()

        self.add_required_resource(
            k8s_platform.K8SResource(
                name=f'{self.name}-gpg-pub-keys',
                definition=textwrap.dedent(f'''\
                    apiVersion: v1
                    type: Opaque
                    kind: Secret
                    data:
                        edgedb.asc: {signing_public_keydata}
                    metadata:
                        name: {self.name}-gpg-pub-keys
                ''')
            )
        )

        self.add_required_resource(gcp_platform.ServiceAccount(
            name='cloudstorage-mount-bot',
            description='Service Account for Cloud Storage Mounts',
            roles=('roles/storage.admin',),
            key_in_secret=f'cloudstorage-mount-bot-credentials',
        ))

        for fn in ('production.yaml', 'tls.yaml', 'ingress.yaml'):
            with open(defs / fn) as f:
                definition = f.read()

                definition = definition.replace(
                    '<service-name>',
                    self.name,
                )

                definition = definition.replace(
                    '<hostname>',
                    self.hostname,
                )

                definition = definition.replace(
                    '<hostname-ident>',
                    self.hostname.replace('.', '-').strip('-'),
                )

                definition = definition.replace(
                    '<env>',
                    env.tag,
                )

            name = f'{self.name}-{pathlib.Path(fn).stem}'
            self.add_required_resource(
                k8s_platform.K8SResource(
                    name=name,
                    definition=definition
                )
            )
