"""Workflow for the estimation of conductivity."""
from aiida import orm
# from aiida.engine import ToContext
from aiida.engine import WorkChain

from aiida_finales.calculations import conductivity_estimation


class ConductivityEstimationWorkchain(WorkChain):
    """This workflow represents a process containing a variable number of steps."""

    @classmethod
    def define(cls, spec):
        """Define the process specification."""
        # yapf: disable
        super().define(spec)

        spec.input(
            'input_data',
            valid_type=orm.Dict,
            help='Input data.'
        )

        spec.output(
            'output_data',
            valid_type=orm.Dict,
            help='Output data.'
        )

        spec.outline(
            cls.execute_procedure,
            # cls.gather_results,
        )

    @classmethod
    def get_builder_from_inputs(cls, input_data):
        """Create the builder from the inputs."""
        builder = cls.get_builder()
        parameters = input_data['request']['parameters']['molecular_dynamics']
        if len(parameters['formulation']) == 0:
            return None
        builder.input_data = orm.Dict(dict=input_data)
        return builder

    def execute_procedure(self):
        """Submit the calculation."""
        output_node = conductivity_estimation(input_node=self.inputs.input_data)
        self.out('output_data', output_node)
#
# I get a 'cannot submit a process function'. What is up with that???
#
#    def execute_procedure(self):
#        """Submit the calculation."""
#        inputs = {'input_node': self.inputs.input_data}
#        calculation_node = self.submit(conductivity_estimation, **inputs)
#        self.report(f'launching conductivity_estimation<{calculation_node.pk}>')
#        return ToContext(procedure=calculation_node)
#
#    def gather_results(self):
#        """Take the results and expose them."""
#        self.out('output_data', self.ctx.calculation_node.outputs.result)
