import logging

from amadeus.compositions.statements import base


LOG = logging.getLogger(__name__)


class LoopStatement(base.BaseStatement):
    args = ['int']

    def __init__(self, conf, method, args, returns):
        super(LoopStatement, self).__init__(conf, method, args, returns)

    def run(self):
        try:  # attempt integer loop
            self.loop = int(self.args[0])
            for _ in xrange(self.loop):
                for stmt in self.substatements:
                    stmt.run()
            return
        except ValueError:
            pass
        src = self.args[0]
        if self.args[0] in self.parameters:
            src = self.parameters[self.args[0]]
        for item in src:
            for stmt in self.substatements:
                stmt.run()
