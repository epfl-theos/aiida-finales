"""Module with a utility function to create a result."""


def create_result(value, temp, formulation, calcjob_uuid):
    """Create result object from the conductivity value."""
    method_meta = {
        'success': True,
        'rating': 2,
    }

    conductivity_output = {
        'values': [value],
        'temperature': temp,
        'meta': method_meta,
    }

    run_info = {
        'formulation': formulation,
        'internal_reference': calcjob_uuid,
    }

    result_object = {
        'run_info': run_info,
        'conductivity': conductivity_output,
    }

    return result_object


def wrap_results(quantity, method, request_params, result_object, tenant_uuid,
                 request_uuid):
    """Wrap the result object to submit to FINALES."""
    result_message = {
        'data': result_object,
        'quantity': quantity,
        'method': [method],
        'parameters': request_params,
        'tenant_uuid': tenant_uuid,
        'request_uuid': request_uuid,
    }
    return result_message
