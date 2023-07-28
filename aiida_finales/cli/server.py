"""Commands that act directly on the server."""
import getpass

import click

from aiida_finales.engine.client import FinalesClientConfig

from .root import cmd_root


@cmd_root.group('server')
def cmd_server():
    """Direct queries to the server."""


@cmd_server.command('capabilities')
@click.option(
    '-c',
    '--config-file',
    help='Path to the file with the configuration for the client.',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_tenant_start(config_file):
    """Start up the client (blocks the terminal)."""
    finales_client_config = FinalesClientConfig.load_from_yaml_file(
        config_file)
    connection_manager = finales_client_config.create_client()

    username = finales_client_config.username
    password = getpass.getpass(
        prompt=f'Password for username `{username}` (hidden): ')
    connection_manager.authenticate(username, password)

    click.echo(
        f'Listing capabilities in the server {finales_client_config.host}:')
    capability_list = connection_manager.get_capabilities()
    for capability_data in capability_list:
        quantity = capability_data['quantity']
        method = capability_data['method']
        click.echo(f' > Quantity: `{quantity}` --> Method: `{method}`')
