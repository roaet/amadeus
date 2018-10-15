from amadeus.compositions.statements import base
from amadeus.compositions.statements import loop


class StatementFactory(object):
    def __init__(self, configuration, parameters):
        self.configuration = configuration
        self.parameters = parameters

    def make_statement(self, definition):
        if definition.startswith('loop('):
            return loop.LoopStatement(
                definition, self.configuration, self.parameters)
        return base.BaseStatement(
            definition, self.configuration, self.parameters)
