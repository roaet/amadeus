from amadeus.compositions.statements import base
from amadeus.compositions.statements import loop


KNOWN_STATEMENTS = {
    'loop': loop.LoopStatement
}


class StatementFactory(object):
    def __init__(self, conf, parameters=None):
        self.conf = conf
        self.parameters = parameters

    def has_statement(self, name):
        return name in KNOWN_STATEMENTS

    def make_statement(self, name, arguments, returns):
        Statement = KNOWN_STATEMENTS.get(name, base.BaseStatement)
        return Statement(self.conf, name, arguments, returns)
