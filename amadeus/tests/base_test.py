import unittest2

from mock import patch


class AmadeusTestBase(unittest2.TestCase):
    def create_patch(self, name, func=None):
        patcher = patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing
