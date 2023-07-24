"""Main client."""
import time

from aiida import orm
from aiida.engine import submit

from aiida_finales.calculations import conductivity_estimation
from aiida_finales.client import schemas
from aiida_finales.workflows import ConductivityEstimationWorkchain

TENANT_CAPABILITIES = {
    'testum': ConductivityEstimationWorkchain,
}


class AiidaTenant:
    """Main tenant class."""

    def __init__(self, finales_client):
        """Initialize the tenant."""
        self._client = finales_client

    def start(finales_client):
        """Start up the client (blocks the terminal)."""
        processed_requests = set()
        ongoing_requests = dict()

        while True:
            # LOAD ALL CURRENT WORKFLOWS AND THEIR REQUEST IDS
            #  > Check if anything is finished and post results

            # GET THE REQUESTS FROM THE SERVER AND CHECK
            #  > Which ones can be done
            #  > Which ones are not already in process

            print(' > Next loop starts in 5 seconds...')
            time.sleep(5)

            # IDEA = use extras instead of having to keep track in memory
            # list_of_processes = aiida_process_list()

            print(' > Looking for conductivity simulations to do...')
            pending_requests = finales_client.get_pending_requests(
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
                    f' > Submited aiida calc for {request_id} (UUID={aiida_uuid})'
                )
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
                    post_answer = finales_client.post_measurment(
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
    calculation_node = submit(conductivity_estimation,
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
