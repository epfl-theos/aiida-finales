"""Commands to handle the finale client."""
# pylint: disable=too-many-locals
import getpass

import click

from aiida import load_profile

from aiida_finales.engine.client import FinalesClientConfig
from aiida_finales.engine.tenant import AiidaTenant

from .root import cmd_root


@cmd_root.group('tenant')
def cmd_tenant():
    """Handle the tenant."""


@cmd_tenant.command('start')
@click.option(
    '-p',
    '--profile',
    help='Name of the AiiDA profile to use (current one by default).',
    required=False,
    type=str,
)
@click.option(
    '-c',
    '--config-file',
    help='Path to the file with the configuration for the client.',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_tenant_start(profile, config_file):
    """Start up the client (blocks the terminal)."""
    load_profile(profile)

    finales_client_config = FinalesClientConfig.load_from_yaml_file(
        config_file)
    connection_manager = finales_client_config.create_client()

    username = finales_client_config.username
    password = getpass.getpass(
        prompt=f'Password for username `{username}` (hidden): ')
    connection_manager.authenticate(username, password)

    aiida_tenant = AiidaTenant(connection_manager)
    aiida_tenant.start()
