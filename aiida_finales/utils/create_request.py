"""Module with a utility function to create a request."""
import uuid

CHEMICALS = {
    'LiPF6': {
        'SMILES': '[Li+].F[P-](F)(F)(F)(F)F',
        'InChIKey': 'AXPLOJNSKRXQPA-UHFFFAOYSA-N',
    },
    'EC': {
        'SMILES': 'C1COC(=O)O1',
        'InChIKey': 'KMTRUDSVKNLOMY-UHFFFAOYSA-N',
    },
    'PC': {
        'SMILES': 'CC1COC(=O)O1',
        'InChIKey': 'RUOJZAUFBMNUDX-UHFFFAOYSA-N',
    },
}


def create_request(temp=None, conc_li=None, conc_ec=None, conc_pc=None):
    """Create request from simplified inputs."""
    method_params = {'formulation': []}

    if temp is not None:
        method_params['temperature'] = temp

    if conc_li is not None:
        component = setup_component('LiPF6', conc_li)
        method_params['formulation'].append(component)

    if conc_ec is not None:
        component = setup_component('EC', conc_ec)
        method_params['formulation'].append(component)

    if conc_pc is not None:
        component = setup_component('PC', conc_pc)
        method_params['formulation'].append(component)

    request_dict = {
        'quantity': 'conductivity',
        'methods': ['molecular_dynamics'],
        'parameters': {
            'molecular_dynamics': method_params
        },
        'tenant_uuid': str(uuid.uuid4()),
    }
    return request_dict


def setup_component(chemical_name, fraction):
    """Set up a dict for component."""
    component_dict = {
        'chemical': CHEMICALS[chemical_name],
        'fraction': fraction,
        'fraction_type': 'molar fraction',
    }
    return component_dict
