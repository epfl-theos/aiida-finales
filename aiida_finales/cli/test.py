"""Commands for testing purposes."""
# pylint: disable=too-many-locals,
import getpass

import click

from aiida_finales.engine.client import FinalesClientConfig
from aiida_finales.utils.conductivity_estimator import estimate_conductivity
from aiida_finales.utils.create_request import create_request
from aiida_finales.utils.create_result import create_result, wrap_results

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

    request_data = create_request(temp=250,
                                  conc_li=0.1,
                                  conc_ec=0.25,
                                  conc_pc=0.65)

    server_reply = connection_manager.post_request(request_data)
    print(server_reply)


@cmd_test.command('post-result')
@click.option(
    '-r',
    '--request-uuid',
    help='UUID of the request being addressed.',
    required=True,
    type=str,
)
@click.option(
    '-c',
    '--config-file',
    help='Path to the file with the configuration for the client.',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_test_postresult(request_uuid, config_file):
    """Post an example response."""
    import uuid

    finales_client_config = FinalesClientConfig.load_from_yaml_file(
        config_file)
    connection_manager = finales_client_config.create_client()

    username = finales_client_config.username
    password = getpass.getpass(
        prompt=f'Password for username `{username}` (hidden): ')
    connection_manager.authenticate(username, password)

    server_reply = connection_manager.get_specific_request(request_uuid)

    request_params = server_reply['request']['parameters']
    data = request_params['molecular_dynamics']

    components = {}
    for component in data['formulation']:
        key = component['chemical']['InChIKey']
        components[key] = component['fraction']

    value_lpf = components.get('AXPLOJNSKRXQPA-UHFFFAOYSA-N', 0.0)
    value_ecs = components.get('KMTRUDSVKNLOMY-UHFFFAOYSA-N', 0.0)
    value_pcs = components.get('RUOJZAUFBMNUDX-UHFFFAOYSA-N', 0.0)
    temp = data.get('temperature', 298)

    result = estimate_conductivity(value_lpf, value_ecs, value_pcs, temp)

    result_data = create_result(result, temp, data['formulation'],
                                str(uuid.uuid4()))
    result_object = wrap_results(
        'conductivity',
        'molecular_dynamics',
        request_params,
        result_data,
        str(uuid.uuid4()),
        request_uuid,
    )

    server_reply = connection_manager.post_result(data=result_object,
                                                  request_id=request_uuid)
    print(server_reply.json)
    return
