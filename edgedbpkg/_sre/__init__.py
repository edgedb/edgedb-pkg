##
# Copyright (c) 2017-present MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import pathlib

from edbsre import resources
from edbsre.lib import services
from edbsre.envs import edgedb1_prod
from edbsre.platform import k8s as k8s_platform


class PubPackagesService(services.Service):

    name = 'pub-packages'
    description = 'Service for EdgeDB release packages'
    hostname = 'packages.{env}.edgedatabase.net'

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

        for fn in ('preparation.yaml', 'production.yaml', 'tls.yaml',
                   'ingress.yaml'):
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
