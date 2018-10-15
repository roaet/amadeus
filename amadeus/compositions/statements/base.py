import logging


LOG = logging.getLogger(__name__)


class BaseStatement(object):
    def __init__(self, definition, conf, parameters):
        self.conf = conf
        self.definition = definition
        self.original_definition = self.definition
        self.substatements = []
        self.args = []
        self.parse_arg_list()
        self.parameters = parameters

    def _output_str(self, level=1):
        out = self.definition
        for stmt in self.substatements:
            out = "%s\n%s%s" % (
                out, '    ' * level, stmt._output_str(level + 1))
        return out

    def _parse_arg_list(self):
        pieces = self.original_definition.split('(', 2)
        if len(pieces) == 1:  # no args
            return
        if not pieces[1].endswith(')'):  # mismatched parenthesis
            LOG.debug("Mismatched parenthesis")
            return
        self.definition = pieces[0]
        self.arg_str = pieces[1][:-1]
        self.args = self.arg_str.split()

    def add_substatement(self, stmt):
        self.substatements.append(stmt)

    def parse_arg_list(self):
        # P = parser.CompositionParser()
        # poo = arglist.parseString(self.original_definition)
        pass

    def __repr__(self):
        return self._output_str()

    def run(self):
        LOG.debug("Running %s with %s" % (self.definition, self.args))
        af = self.conf['action_factory']
        action = af.get_action(self.definition)
        action(self.definition, *self.args)
        for stmt in self.substatements:
            stmt.run()
