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

        for k, v in self.conf.iteritems():
            self._known_identifiers.add(k)

        quotedString = pp.sglQuotedString | pp.dblQuotedString
        identifier = (
            pp.Word( pp.alphas + '_', pp.alphanums + '_' ).setParseAction(
                lambda s, l, t: self.identifiers.append(t[0])
            ))
        validArgs = identifier | quotedString
        arglist = pp.delimitedList( validArgs ).setParseAction(
                lambda s,l,t: self.arguments.extend(t)
            )
        returnChar = pp.Suppress('=>') + identifier
        returnChar.setParseAction(
                lambda s,l,t: self.returns.extend(t))
        method = identifier + pp.FollowedBy('(')
        method.setParseAction(
                lambda s,l,t: setattr(self, 'method', t[0]))
        statement = (
            method + pp.Suppress('(') +
            pp.Optional( arglist ) + pp.Suppress(')'))
        statementWithReturn = (
            statement + pp.Optional( returnChar) 
            )

        self.bnf = statementWithReturn

    def forget(self):
        self._known_identifiers = set([])

        for k, v in self.conf.iteritems():
            self._known_identifiers.add(k)

    def _reset_containers(self):
        self.method = None
        self.identifiers = []
        self.arguments = []
        self.returns = []

    def parse(self, target_string):
        self._reset_containers()
        toks = self.bnf.parseString(target_string, parseAll=True)
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

        for r in self.returns:
            self._known_identifiers.add(r)

        for a in [x for x in self.arguments if x in self.identifiers]:
            if a not in self._known_identifiers:
                LOG.warning("%s : %s is an unknown argument passed to %s" % (
                    target_string, a, self.method))
                count += 1

        if count == 0:
            LOG.debug("%s : OK :)" % target_string)

        return {
            'method': self.method,
            'identifiers': self.identifiers,
            'arguments': self.arguments,
            'returns': self.returns
        }


class ParserTester(runnable.Runnable):
    def __init__(self):
        super(ParserTester, self).__init__(False)

    def run(self):
        conf = {'woofle': 'poop'}
        P = CompositionParser(conf)
        checks = [
            'extract()',
            'fx2("stringZ")',
            'fx3(arg1)',
            'fx4("stringA", "stringB")',
            'fx5() => ret',
            'fx5a()=>arg2',
            'fx6("string1", "string2", arg2) => return2',
        ]
        checks2 = [
            'extract(poop)',
            'extract("poop")',
            'extract(woofle)',
        ]
        for chk in [checks, checks2]:
            for s in chk:
                P.parse(s)
            P.forget()


if __name__ == '__main__':
    ParserTester().run()
