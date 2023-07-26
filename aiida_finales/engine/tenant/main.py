"""Main client."""
import time

from aiida import orm
from aiida.engine import submit

from aiida_finales.calculations import conductivity_estimation
from aiida_finales.engine.client import schemas
from aiida_finales.workflows import ConductivityEstimationWorkchain

TENANT_CAPABILITIES = {
    'conductivity': {
        'molecular_dynamics': ConductivityEstimationWorkchain
    },
}


class AiidaTenant:
    """Main tenant class."""

    def __init__(self, finales_client):
        """Initialize the tenant."""
        self._client = finales_client

    def start(self):
        """Start up the client (blocks the terminal)."""
        while True:

            print(' > Waiting to start the next loop...')
            time.sleep(3)

            print(' > Querying AiiDA processes...')
            requests_ongoing = self.query_requests_ongoing()
            requests_finished = self.query_requests_finished()

            print(' > Looking for requests in the server...')
            pending_requests = self._client.get_pending_requests()

            print(' > Updating finished requests...')
            outstanding_requests = {}
            for request_data in pending_requests:

                request_id = request_data['uuid']

                if request_id in requests_ongoing:
                    continue

                if request_id in requests_finished:
                    self.submit_results(request_id,
                                        requests_finished[request_id])
                    continue

                prepared_submission = self.prepare_submission(request_data)
                if prepared_submission is not None:
                    outstanding_requests[request_id] = prepared_submission

            print(' > Launching new requests...')
            for request_id, request_data in outstanding_requests.items():
                self.launch_process(request_id, request_data)

    def query_requests_ongoing(self):
        """Get all processes that are still ongoing."""
        time.sleep(1)
        return {}

    def query_requests_finished(self):
        """Get all processes that are finished."""
        time.sleep(1)
        return {}

    def prepare_submission(self, request_data):
        """Check if the tenant can deal with the request."""
        print(f'Received {request_data}')

        request_quantity = request_data['request']['quantity']
        if request_quantity not in TENANT_CAPABILITIES:
            return None

        request_methods = request_data['request']['methods']

        for method_name in request_methods:

            if method_name not in TENANT_CAPABILITIES[request_quantity]:
                continue

            MethodClass = TENANT_CAPABILITIES[request_quantity][method_name]
            method_params = request_data['request']['parameters'][method_name]
            builder = MethodClass.get_builder_from_inputs(method_params)

            if builder is not None:
                return builder

        return None

    def submit_results(self, request_id, workflow):
        """Submit the results to the server."""
        print(f'Received {request_id} and {workflow}')
        time.sleep(1)

    def launch_process(self, request_id, request_data):
        """Launch a process to address the request."""
        print(f'Received {request_id} and {request_data}')
        time.sleep(1)


#            print(' > Looking for conductivity simulations to do...')
#            pending_requests = finales_client.get_pending_requests(
#                params={'fom_name': 'conductivity'})
#            accepted_requests = filter_requests(pending_requests,
#                                                processed_requests)
#
#            print(' > Measurement requests found:')
#            for reqid in pending_requests.keys():
#                is_valid = reqid in accepted_requests
#                print(f' >>> {reqid} (accepted? = {is_valid})')
#            print(' >')
#
#            for request_id, request_data in accepted_requests.items():
#                aiida_uuid = submit_aiida_process(request_data, request_id)
#                print(
#                    f' > Submited aiida calc for {request_id} (UUID={aiida_uuid})'
#                )
#                processed_requests.add(request_id)
#                ongoing_requests[aiida_uuid] = set_request_response_data(
#                    request_id, request_data)
#
#            list_to_remove = []
#            for aiida_uuid, extra_data in ongoing_requests.items():
#                reqid = extra_data['request_id']
#                print(
#                    f' > Checking on aiida process {aiida_uuid} for request {reqid}'
#                )
#                result = check_aiida_result(aiida_uuid)
#
#                if result is not None:
#                    fom = schemas.FomData(values=result,
#                                          dim=1,
#                                          **extra_data['fomdata_init'])
#                    post_data = schemas.Measurement(
#                        fom_data=[fom], **extra_data['measurement_init'])
#                    post_answer = finales_client.post_measurment(
#                        reqid, post_data.json())
#
#                    print(
#                        f' > Finished {aiida_uuid} for {reqid}:\n >>> {post_answer}'
#                    )
#                    list_to_remove.append(aiida_uuid)
#
#            print(list_to_remove)
#            for aiida_uuid in list_to_remove:
#                ongoing_requests.pop(aiida_uuid)
#
#            print(
#                '-----------------------------------------------------------------------------'
#            )


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
