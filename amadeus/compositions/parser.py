import logging

import pyparsing as pp

from amadeus import action_factory
from amadeus import runnable


LOG = logging.getLogger(__name__)


class CompositionParser(object):
    def __init__(self, configuration):
        self.conf = configuration
        self.AF = action_factory.ActionFactory(self.conf)
        self._reset_containers()
        self._known_identifiers = set([])
        self._preload_known_identifiers()
        self._define_grammar()

    def _define_grammar(self):
        quotedString = pp.sglQuotedString | pp.dblQuotedString
        identifier = (
            pp.Word(pp.alphas + '_', pp.alphanums + '_').setParseAction(
                lambda s, l, t: self.identifiers.append(t[0])))
        validArgs = identifier | quotedString
        arglist = pp.delimitedList(validArgs).setParseAction(
            lambda s, l, t: self.arguments.extend(t))
        returnChar = pp.Suppress('=>') + identifier
        returnChar.setParseAction(
            lambda s, l, t: self.returns.extend(t))
        method = identifier + pp.FollowedBy('(')
        method.setParseAction(
            lambda s, l, t: setattr(self, 'method', t[0]))
        statement = (
            method + pp.Suppress('(') +
            pp.Optional(arglist) + pp.Suppress(')'))
        statementWithReturn = (
            statement + pp.Optional(returnChar))

        self.bnf = statementWithReturn

    def _preload_known_identifiers(self):
        for k, v in self.conf.iteritems():
            self._known_identifiers.add(k)

    def _reset_containers(self):
        self.method = None
        self.identifiers = []
        self.arguments = []
        self.returns = []

    def forget(self):
        self._known_identifiers = set([])
        self._preload_known_identifiers()

    def parse(self, target_string, strict=False):
        self._reset_containers()
        self.bnf.parseString(target_string, parseAll=True)
        self._known_identifiers.add(self.method)
        count = 0
        if self.AF.has_action(self.method):
            Action = self.AF.get_action(self.method)
            if len(Action.args) > len(self.arguments):
                LOG.warning(
                    "%s : %s takes at least %d argument but %d given" % (
                        target_string, self.method,
                        len(Action.args), len(self.arguments)))
                count += 1
        else:
            LOG.warning("%s : Unknown action %s" % (
                target_string, self.method))
            count += 1

        for a in [x for x in self.arguments if x in self.identifiers]:
            if a not in self._known_identifiers:
                LOG.warning("%s : %s is an unknown argument passed to %s" % (
                    target_string, a, self.method))
                count += 1

        for r in self.returns:
            self._known_identifiers.add(r)

        if count == 0:
            LOG.debug("%s : OK :)" % target_string)

        return {
            'success': count == 0,
            'method': self.method,
            'identifiers': self.identifiers,
            'arguments': self.arguments,
            'returns': self.returns
        }
