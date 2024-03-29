"""Main client."""
import time
import uuid

from aiida import orm
from aiida.engine import submit

from aiida_finales.workflows import ConductivityEstimationWorkchain

TENANT_CAPABILITIES = {
    'conductivity': {
        'molecular_dynamics': {
            'class':
            ConductivityEstimationWorkchain,
            'process_type':
            'aiida_finales.workflows.conductivity_estimation.ConductivityEstimationWorkchain',
        }
    },
}


class AiidaTenant:
    """Main tenant class."""

    def __init__(self, finales_client, tenant_uuid=None):
        """Initialize the tenant."""
        self._client = finales_client
        self._tenant_uuid = tenant_uuid
        if self._tenant_uuid is None:
            self._tenant_uuid = str(uuid.uuid4())

    def start(self):
        """Start up the client (blocks the terminal)."""
        while True:

            print(' > Waiting to start the next loop...')
            time.sleep(3)

            print(' > Querying AiiDA processes...')
            requests_submitted = self.query_requests_submitted()

            print(' > Looking for requests in the server...')
            pending_requests = self._client.get_pending_requests()
            print(f' >>> Received {len(pending_requests)} requests!')

            print(' > Updating finished requests...')
            outstanding_requests = {}
            for request_data in pending_requests:

                request_id = request_data['uuid']

                if request_id in requests_submitted['excepted']:
                    workflow_node = requests_submitted['excepted'][request_id]
                    print(
                        f' >>> Request {request_id} had a problem in workflow {workflow_node.pk}'
                    )
                    continue

                if request_id in requests_submitted['ongoing']:
                    workflow_node = requests_submitted['ongoing'][request_id]
                    print(
                        f' >>> Request {request_id} already in process by workflow {workflow_node.pk}'
                    )
                    continue

                if request_id in requests_submitted['finished']:
                    workflow_node = requests_submitted['finished'][request_id]
                    print(
                        f' >>> Reporting back workflow {workflow_node.pk} for request {request_id}'
                    )
                    self.submit_results(request_data, workflow_node)
                    continue

                prepared_submission = self.prepare_submission(request_data)
                if prepared_submission is not None:
                    outstanding_requests[request_id] = prepared_submission

            print(' > Launching new requests...')
            for request_id, request_process in outstanding_requests.items():
                print(f' >>> Launching processs for request {request_id}')
                process_node = submit(request_process)
                process_node.base.extras.set('request_uuid', request_id)

    def query_requests_submitted(self):
        """Get all processes that have already been submitted."""
        relevant_types = []
        for key_q, methods in TENANT_CAPABILITIES.items():
            for key_m, data in methods.items():
                relevant_types.append(data['process_type'])

        queryb = orm.QueryBuilder()
        queryb.append(orm.WorkflowNode,
                      filters={'process_type': {
                          'in': relevant_types
                      }})

        submitted_requests = {
            'ongoing': {},
            'finished': {},
            'excepted': {},
        }
        for workflow_node in queryb.all(flat=True):

            request_id = workflow_node.extras['request_uuid']

            if workflow_node.is_finished_ok:
                submitted_requests['finished'][request_id] = workflow_node

            elif workflow_node.is_excepted or workflow_node.is_failed:
                if request_id not in submitted_requests['excepted']:
                    submitted_requests['excepted'][request_id] = []
                submitted_requests['excepted'][request_id].append(
                    workflow_node)

            else:
                submitted_requests['ongoing'][request_id] = workflow_node

        return submitted_requests

    def prepare_submission(self, request_data):
        """Check if the tenant can deal with the request."""
        request_quantity = request_data['request']['quantity']
        if request_quantity not in TENANT_CAPABILITIES:
            return None

        request_methods = request_data['request']['methods']

        for method_name in request_methods:

            if method_name not in TENANT_CAPABILITIES[request_quantity]:
                continue

            MethodClass = TENANT_CAPABILITIES[request_quantity][method_name][
                'class']
            builder = MethodClass.get_builder_from_inputs(request_data)

            if builder is not None:
                return builder

        return None

    def submit_results(self, request_data, workflow_node):
        """Submit the results to the server."""
        from aiida_finales.utils.create_result import wrap_results
        result_data = workflow_node.outputs.output_data.get_dict()
        method = 'molecular_dynamics'  # This should be generalized...
        wrapped_results = wrap_results(request_data, result_data, method,
                                       self._tenant_uuid)
        server_reply = self._client.post_result(
            data=wrapped_results, request_id=request_data['uuid'])
        print(server_reply)
