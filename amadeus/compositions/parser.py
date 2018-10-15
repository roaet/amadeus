import logging

import pyparsing as pp
from pyparsing import alphanums

from pyparsing import alphas
from pyparsing import dblQuotedString
from pyparsing import delimitedList
from pyparsing import nums
from pyparsing import sglQuotedString

from pyparsing import FollowedBy
from pyparsing import Optional
from pyparsing import Suppress
from pyparsing import Word

from amadeus.actions import factory as action_factory
from amadeus.compositions.statements import factory as stmt_factory


LOG = logging.getLogger(__name__)


class CompositionParser(object):
    def __init__(self, conf):
        self.conf = conf
        self.AF = action_factory.ActionFactory(self.conf)
        self.SF = stmt_factory.StatementFactory(self.conf)
        self._reset_containers()
        self._known_identifiers = set([])
        self._preload_known_identifiers()
        self._define_grammar()

    def _define_grammar(self):
        number = Word(nums) + Optional('.' + Word(nums))
        quotedString = sglQuotedString | dblQuotedString
        identifier = (
            Word(alphas + '_', alphanums + '_').setParseAction(
                lambda s, l, t: self.identifiers.append(t[0])))
        validArgs = identifier | quotedString | number
        arglist = delimitedList(validArgs).setParseAction(
            lambda s, l, t: self.arguments.extend(t))
        returnChar = Suppress('=>') + identifier
        returnChar.setParseAction(
            lambda s, l, t: self.returns.extend(t))
        method = identifier + FollowedBy('(')
        method.setParseAction(
            lambda s, l, t: setattr(self, 'method', t[0]))
        statement = (
            method + Suppress('(') +
            Optional(arglist) + Suppress(')') +
            Optional(Suppress(':')))
        statementWithReturn = (
            statement + Optional(returnChar))

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
        try:
            self.bnf.parseString(target_string, parseAll=True)
        except pp.ParseException as e:
            LOG.error("Error parsing '%s': %s" % (target_string, e))
            raise e
        self._known_identifiers.add(self.method)

        Thing = None
        count = 0
        if self.SF.has_statement(self.method):
            Thing = self.SF.make_statement(
                self.method, self.arguments, self.returns)
        elif self.AF.has_action(self.method):

            Thing = self.AF.get_action(self.method)
        if Thing is not None:
            if len(Thing.args) > len(self.arguments):
                LOG.warning(
                    "%s : %s takes at least %d argument but %d given" % (
                        target_string, self.method,
                        len(Thing.args), len(self.arguments)))
                count += 1
        else:
            LOG.warning("%s : Unknown method %s" % (
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
