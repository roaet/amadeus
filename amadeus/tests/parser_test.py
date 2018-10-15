from amadeus.compositions import parser
from amadeus.tests import base_test as base


class TestAction(object):
    def __init__(self, args=[]):
        self.args = args


class EYAMLParserTest(base.AmadeusTestBase):
    def setUp(self):
        super(EYAMLParserTest, self).setUp()
        self.conf = {}
        self.parser = parser.CompositionParser(self.conf)
        self.expected_keys = [
            'success', 'method', 'identifiers', 'arguments', 'returns']

    def setup_mocks(self, fx_info_dict):
        af_mock_has = self.create_patch(
            'amadeus.action_factory.ActionFactory.has_action')
        af_mock_has.side_effect = lambda x: x in fx_info_dict

        af_mock_get = self.create_patch(
            'amadeus.action_factory.ActionFactory.get_action')

        fake_actions = {}
        for fx_name, args in fx_info_dict.iteritems():
            fake_actions[fx_name] = TestAction(['str'])
        af_mock_get.side_effect = lambda x: fake_actions.get(x)

    def basic_pretest(self, test):
        ret = self.parser.parse(test)
        self.assertIsNotNone(ret, 'parse(%s) returned None' % test)
        self.assertTrue(
            all([x in ret for x in self.expected_keys]),
            'parse(%s) was missing keys' % test)
        return ret

    def is_good(self, test):
        ret = self.basic_pretest(test)
        self.assertTrue(
            ret['success'], "%s expected to be good, but was not" % test)

    def is_bad(self, test):
        ret = self.basic_pretest(test)
        self.assertFalse(
            ret['success'], "%s expected to be bad, but was not" % test)

    def test_expected_successes(self):
        self.setup_mocks({'known_fx': ['str']})
        self.is_good("known_fx('asdf')")
        self.is_good("known_fx('asdf'):")
        self.is_good("known_fx('asdf') => ret")
        self.is_good("known_fx(ret) => ret2")

    def test_expected_fails(self):
        self.is_bad("known_fx('asdf')")
        self.setup_mocks({'known_fx': ['str']})
        self.is_good("known_fx('asdf')")
        self.is_bad("known_fx(ret) => ret")
        self.is_good("known_fx('asdf') => ret")
        self.is_good("known_fx(ret) => ret2")

    def test_forgetting(self):
        self.setup_mocks({'known_fx': ['str']})
        self.is_good("known_fx('asdf') => ret")
        self.is_good("known_fx(ret) => ret2")
        self.parser.forget()
        self.is_bad("known_fx(ret) => ret2")
