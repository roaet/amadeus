import logging

from amadeus.actions import factory as action_factory


LOG = logging.getLogger(__name__)


class BaseStatement(object):
    def __init__(self, conf, method, args, returns):
        self.conf = conf
        self.method = method
        self.args = args
        self.returns = returns
        self.substatements = []
        self.AF = action_factory.ActionFactory(self.conf)

    def run(self):
        LOG.debug("Running %s with %s" % (self.method, self.args))

        kwargs = {'returns': self.returns}
        self.AF(self.method, *self.args, **kwargs)
        for stmt in self.substatements:
            stmt.run()
        return

    def add_substatement(self, stmt):
        self.substatements.append(stmt)

    def _output_str(self, level=1):
        out = "%s(%s) => %s" % (self.method, self.args, self.returns)
        for stmt in self.substatements:
            out = "%s\n%s%s" % (
                out, '    ' * level, stmt._output_str(level + 1))
        return out

    def __repr__(self):
        return self._output_str()
