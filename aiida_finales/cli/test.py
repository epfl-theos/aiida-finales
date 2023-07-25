"""Commands for testing purposes."""
# pylint: disable=too-many-locals,
import getpass

import click

from aiida_finales.engine.client import FinalesClientConfig, schemas
from aiida_finales.utils.create_request import create_request

from .root import cmd_root


@cmd_root.group('test')
def cmd_test():
    """Commands for testing purposes."""


@cmd_test.command('connection')
@click.option(
    '-c',
    '--config-file',
    help='Path to the file with the configuration for the client.',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_test_connection(config_file):
    """Populate the server with test requests."""
    import requests
    finales_client_config = FinalesClientConfig.load_from_yaml_file(
        config_file)
    host = finales_client_config.host
    port = finales_client_config.port
    connection_url = f'http://{host}:{port}/docs'
    reply = requests.get(connection_url)
    click.echo(f'Response should be 200. Response: `{reply.status_code}`')


@cmd_test.command('populate')
@click.option(
    '-c',
    '--config-file',
    help='Path to the file with the configuration for the client.',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_test_populate(config_file):
    """Populate the server with test requests."""
    finales_client_config = FinalesClientConfig.load_from_yaml_file(
        config_file)
    connection_manager = finales_client_config.create_client()

    username = finales_client_config.username
    password = getpass.getpass(
        prompt=f'Password for username `{username}` (hidden): ')
    connection_manager.authenticate(username, password)

    request_data = create_request(temp=298,
                                  conc_li=0.05,
                                  conc_ec=0.45,
                                  conc_pc=0.5)
    server_reply = connection_manager.post_request(request_data)
    print(server_reply)
    return

    print(' > Logging in (takes 5 seconds) ...')
    connection_manager.authenticate()

    list_of_compositions = [
        {
            'lpf': 6.0,
            'pcs': 6.0,
            'ecs': 4.0
        },
        {
            'lpf': 2.0,
            'pcs': 3.3,
            'ecs': 6.7
        },
    ]

    ids = []
    for composition in list_of_compositions:

        chemicals = [
            schemas.Chemical(smiles='[Li+].F[P-](F)(F)(F)(F)F',
                             name='LiPF6',
                             reference='LiPF6_ref'),
            schemas.Chemical(smiles='CC1COC(=O)O1',
                             name='PC',
                             reference='PC_ref'),
            schemas.Chemical(smiles='C1COC(=O)O1',
                             name='EC',
                             reference='EC_ref'),
        ]

        amounts = [
            {
                'value': composition['lpf'],
                'unit': 'mol'
            },
            {
                'value': composition['pcs'],
                'unit': 'mol'
            },
            {
                'value': composition['ecs'],
                'unit': 'mol'
            },
        ]

        form = schemas.Formulation(
            chemicals=chemicals,
            amounts=amounts,
            ratio_method='molar',
        )

        meas = schemas.Measurement(
            formulation=form,
            temperature=schemas.Temperature(value=303, unit='K'),
            pending=True,
            fom_data=[],
            kind=schemas.Origin(origin='simulation', what='conductivity'),
        )

        ans_ = connection_manager.post_request(json_data=meas.json())
        ids.append(ans_)

    print(ids)
