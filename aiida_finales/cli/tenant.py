"""Commands to handle the finale client."""
# pylint: disable=too-many-locals
import getpass

import click
import yaml  # consider strictyaml for automatic schema validation

from aiida import load_profile

from aiida_finales.engine.client import FinalesClient
from aiida_finales.engine.tenant import tenant_start

from .root import cmd_root


@cmd_root.group('tenant')
def cmd_client():
    """Handle the tenant."""


@cmd_client.command('start')
@click.option(
    '-c',
    '--client-config-file',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_tenant_start(client_config_file):
    """Start up the client (blocks the terminal)."""
    with open(client_config_file) as fileobj:
        try:
            client_config = yaml.load(fileobj, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(
                'Error while trying to read the yaml from client-config-file'
            ) from exc

    client_profile = client_config.get('aiida_profile', None)
    load_profile(client_profile)

    settings = {
        'username': client_config['username'],
        'ipurl': client_config['ip_url'],
        'port': client_config['port'],
    }
    username = settings['username']

    settings['password'] = getpass.getpass(
        prompt=f'Password for username `{username}` (hidden): ')
    connection_manager = FinalesClient(**settings)

    tenant_start(connection_manager)
