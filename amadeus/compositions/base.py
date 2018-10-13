import hashlib
import logging

import numpy as np
import pandas as pd
import pyparsing as pp
from ruamel import yaml

from amadeus import constants
from amadeus.compositions import parser
from amadeus import utils
from amadeus import action_factory as AF
from amadeus import yaml_object as yo


LOG = logging.getLogger(__name__)

TOP_LEVEL_KEY = 'composition'


class BaseStatement(object):
    def __init__(self, definition, conf, parameters):
        self.conf = conf
        self.definition = definition
        self.original_definition = self.definition
        self.substatements = []
        self.args = []
        self.parse_arg_list()
        self.parameters = parameters

    def add_substatement(self, stmt):
        self.substatements.append(stmt)

    def _output_str(self, level=1):
        out = self.definition
        for stmt in self.substatements:
            out = "%s\n%s%s" % (out, '    ' * level, stmt._output_str(level+1)) 
        return out

    def parse_arg_list(self):
        P = parser.CompositionParser()
        import ipdb; ipdb.set_trace()  # noqa
        poo = arglist.parseString(self.original_definition)
        pass

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

    def run(self):
        LOG.debug("Running %s with %s" % (self.definition, self.args))
        af = self.conf['action_factory']
        action = af.get_action(self.definition)
        af(self.definition, *self.args)
        for stmt in self.substatements:
            stmt.run()

    def __repr__(self):
        return self._output_str()


class LoopStatement(BaseStatement):
    def __init__(self, definition, conf, parameters):
        super(LoopStatement, self).__init__(definition, conf, parameters)

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


class StatementFactory(object):
    def __init__(self, configuration, parameters):
        self.configuration = configuration
        self.parameters = parameters

    def make_statement(self, definition):
        if definition.startswith('loop('):
            return LoopStatement(
                definition, self.configuration, self.parameters)
        return BaseStatement(definition, self.configuration, self.parameters)


class BaseComposition(yo.YAMLBackedObject):
    def __init__(self, yaml_obj, conf):
        super(BaseComposition, self).__init__(yaml_obj, conf, TOP_LEVEL_KEY)
        af = AF.ActionFactory(self.conf)
        self.conf['action_factory'] = af
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
        root_stmt = BaseStatement('main()', self.conf, self.vars)
        main = self.yaml_obj.get('main')
        self._parse_node(root_stmt, main)
        return root_stmt

    def _create_statement(self, definition):
        fact = StatementFactory(self.conf, self.vars)
        return fact.make_statement(definition)

    def _parse_node(self, parent, node, level=0):
        for statement in node:
            if type(statement) == dict:
                for k, subnode in statement.iteritems():
                    new_stmt = self._create_statement(k)
                    self._parse_node(new_stmt, subnode, level+1)
            else:
                new_stmt = self._create_statement(statement)
            parent.add_substatement(new_stmt)

    def __repr__(self):
        return "COMP(%s:%s)\n%s" % (self.type, self.name, self.start)

    @staticmethod
    def check(yaml_obj, yaml_file, key=None):
        return yo.YAMLBackedObject.check(
            yaml_obj, yaml_file, TOP_LEVEL_KEY, constants.COMPOSITION_TYPES)
