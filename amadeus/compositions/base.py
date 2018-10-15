import logging

from amadeus import action_factory
from amadeus import constants
from amadeus.compositions import parser
from amadeus.compositions.statements import base
from amadeus.compositions.statements import factory as stmt_factory
from amadeus import yaml_object as yo


LOG = logging.getLogger(__name__)

TOP_LEVEL_KEY = 'composition'


class BaseComposition(yo.YAMLBackedObject):
    def __init__(self, yaml_obj, conf):
        super(BaseComposition, self).__init__(yaml_obj, conf, TOP_LEVEL_KEY)
        self.AF = action_factory.ActionFactory(self.conf)
        self.SF = stmt_factory.StatementFactory(self.conf)
        self.parser = parser.CompositionParser(self.conf)
        self.vars = {}
        self._parse_vars()
        self.start = self._parse_main()

    def run(self):
        self.start.run()

    def _parse_vars(self):
        var_list = self.yaml_obj.get('vars', [])
        for var in var_list:
            for name, values in var.iteritems():
                self.vars[name] = values
        LOG.debug(self.vars)

    def _parse_main(self):
        root_stmt = base.BaseStatement(self.conf, 'main()', [], [])
        main = self.yaml_obj.get('main')
        self._parse_node(root_stmt, main)
        return root_stmt

    def _create_statement(self, definition):
        res = self.parser.parse(definition)
        method = res.get('method')
        args = res.get('arguments', [])
        returns = res.get('returns', [])
        return self.SF.make_statement(method, args, returns)

    def _parse_node(self, parent, node, level=0):
        for statement in node:
            if type(statement) == dict:
                for k, subnode in statement.iteritems():
                    new_stmt = self._create_statement(k)
                    self._parse_node(new_stmt, subnode, level + 1)
            else:
                new_stmt = self._create_statement(statement)
            parent.add_substatement(new_stmt)

    def __repr__(self):
        return "COMP(%s:%s)\n%s" % (self.type, self.name, self.start)

    @staticmethod
    def check(yaml_obj, yaml_file, key=None):
        return yo.YAMLBackedObject.check(
            yaml_obj, yaml_file, TOP_LEVEL_KEY, constants.COMPOSITION_TYPES)
