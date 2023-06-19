# -*- coding: utf-8 -*-
"""Commands to handle the finale client."""
# pylint: disable=too-many-locals
import getpass

import click
import yaml  # consider strictyaml for automatic schema validation

from aiida import load_profile, orm
from aiida.engine import submit

from aiida_finale.calculations import conductivity_calcfunction
from aiida_finale.client import schemas
from aiida_finale.client.connection_manager import ConnectionManager

from .root import cmd_root


@cmd_root.group('client')
def cmd_client():
    """Handle the client."""


@cmd_client.command('start')
@click.option(
    '-c',
    '--client-config-file',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
)
def cmd_client_start(client_config_file):
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
    connection_manager = ConnectionManager(**settings)

    processed_requests = set()
    ongoing_requests = dict()

    while True:
        print(' > Logging in (takes 5 seconds) ...')
        connection_manager.authenticate()

        # IDEA = use extras instead of having to keep track in memory
        # list_of_processes = aiida_process_list()

        print(' > Looking for conductivity simulations to do...')
        pending_requests = connection_manager.get_pending_requests(
            params={'fom_name': 'conductivity'})
        accepted_requests = filter_requests(pending_requests,
                                            processed_requests)

        print(' > Measurement requests found:')
        for reqid in pending_requests.keys():
            is_valid = reqid in accepted_requests
            print(f' >>> {reqid} (accepted? = {is_valid})')
        print(' >')

        for request_id, request_data in accepted_requests.items():
            aiida_uuid = submit_aiida_process(request_data, request_id)
            print(
                f' > Submited aiida calc for {request_id} (UUID={aiida_uuid})')
            processed_requests.add(request_id)
            ongoing_requests[aiida_uuid] = set_request_response_data(
                request_id, request_data)

        list_to_remove = []
        for aiida_uuid, extra_data in ongoing_requests.items():
            reqid = extra_data['request_id']
            print(
                f' > Checking on aiida process {aiida_uuid} for request {reqid}'
            )
            result = check_aiida_result(aiida_uuid)

            if result is not None:
                fom = schemas.FomData(values=result,
                                      dim=1,
                                      **extra_data['fomdata_init'])
                post_data = schemas.Measurement(
                    fom_data=[fom], **extra_data['measurement_init'])
                post_answer = connection_manager.post_measurment(
                    reqid, post_data.json())

                print(
                    f' > Finished {aiida_uuid} for {reqid}:\n >>> {post_answer}'
                )
                list_to_remove.append(aiida_uuid)

        print(list_to_remove)
        for aiida_uuid in list_to_remove:
            ongoing_requests.pop(aiida_uuid)

        print(
            '-----------------------------------------------------------------------------'
        )


################################################################################
def filter_requests(input_requests, processed_requests):
    """Auxiliary function."""
    output_requests = dict()

    for request_id, request_data in input_requests.items():

        is_request_valid = True

        present_compounds = []
        for chemical in request_data['formulation']['chemicals']:
            present_compounds.append(chemical['name'])

        for critical_compound in ['LiPF6', 'PC']:
            if critical_compound not in present_compounds:
                is_request_valid = False

        temperature = request_data['temperature']['value']
        if not 243 <= temperature <= 333:
            is_request_valid = False

        if request_id in processed_requests:
            is_request_valid = False

        if is_request_valid:
            output_requests[request_id] = request_data

    return output_requests


################################################################################
def set_request_response_data(request_id, request_data):
    """Auxiliary function."""
    output_dict = {
        'measurement_init': {
            'formulation': request_data['formulation'],
            'temperature': request_data['temperature'],
            'pending': False,
            'kind': schemas.Origin(origin='simulation'),
        },
        'fomdata_init': {
            'unit': '\u03BC/cm',
            'origin': schemas.Origin(origin='simulation'),
            'measurement_id': '123',
            'name': 'conductivity',
            'internalReference': 'aiida_simulation',
        },
        'request_id': request_id,
    }
    return output_dict


################################################################################
def submit_aiida_process(request_data, request_id):
    """Submit aiida process."""
    input_datanode = orm.Dict(dict=request_data)
    calculation_node = submit(conductivity_calcfunction,
                              input_node=input_datanode)
    calculation_node.base.extras.set('finale_request_id', request_id)
    return calculation_node.uuid


################################################################################
def check_aiida_result(process_uuid):
    """Check aiida process status."""
    calculation_node = orm.load_node(process_uuid)
    result = None
    if calculation_node.is_finished_ok:
        result = calculation_node.outputs.result.get_dict()['values']
        print(result)
    return result


################################################################################
def aiida_process_list():
    """List processess."""
    queryb = orm.QueryBuilder()
    queryb.append(
        orm.ProcessNode,
        filters={'extras': {
            'has_key': 'finale_request_id'
        }},
    )
    return queryb.all(flat=True)
