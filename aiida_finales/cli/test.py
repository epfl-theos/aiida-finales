"""Commands for testing purposes."""
# pylint: disable=too-many-locals,
import getpass

import click
import yaml  # consider strictyaml for automatic schema validation

from aiida_finales.client import schemas
from aiida_finales.client.connection_manager import ConnectionManager

from .root import cmd_root


@cmd_root.group('test')
def cmd_test():
    """Commands for testing purposes."""


@cmd_test.command('populate')
@click.option(
    '-c',
    '--client-config-file',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_test_populate(client_config_file):
    """Populate the server with test requests."""
    with open(client_config_file) as fileobj:
        try:
            client_config = yaml.load(fileobj, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(
                'Error while trying to read the yaml from client-config-file'
            ) from exc

    settings = {
        'username': client_config['username'],
        'ipurl': client_config['ip_url'],
        'port': client_config['port'],
    }
    username = settings['username']

    settings['password'] = getpass.getpass(
        prompt=f'Password for username `{username}` (hidden): ')
    connection_manager = ConnectionManager(**settings)

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
