"""Calculation for the estimation of conductivity."""
from aiida import orm
from aiida.engine import calcfunction

from aiida_finales.utils.conductivity_estimator import estimate_conductivity
from aiida_finales.utils.create_result import create_result


@calcfunction
def conductivity_estimation(input_node):
    """Calculate the conductivity of LiPF6 in EC+PC mixtures."""
    input_data = input_node.get_dict()
    input_params = input_data['request']['parameters']['molecular_dynamics']

    components_fractions = {}
    for component in input_params['formulation']:
        inchikey = component['chemical']['InChIKey']
        components_fractions[inchikey] = component['fraction']

    temp = input_params.get('temperature', 298)
    value_lpf = components_fractions.get('AXPLOJNSKRXQPA-UHFFFAOYSA-N', 0.0)
    value_ecs = components_fractions.get('KMTRUDSVKNLOMY-UHFFFAOYSA-N', 0.0)
    value_pcs = components_fractions.get('RUOJZAUFBMNUDX-UHFFFAOYSA-N', 0.0)

    result_raw = estimate_conductivity(value_lpf, value_ecs, value_pcs, temp)
    result_data = create_result(result_raw, temp, input_params['formulation'],
                                input_node.uuid)
    # NOTE -> result data can't contain the calcjob uuid if I'm creating it inside the calcjob...
    # Using the input node uuid instead while I figure out how to re-arrange this.
    return orm.Dict(dict=result_data)
