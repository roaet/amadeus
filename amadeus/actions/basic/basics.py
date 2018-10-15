import logging

from amadeus.actions.basic import base_action as base


LOG = logging.getLogger(__name__)


class Print(base.BaseAction):
    cmd = 'print'
    args = ['str']

    def __init__(self, configuration):
        super(Print, self).__init__(configuration)

    def run(self, message, **configuration):
        LOG.debug('print: %s' % message)


class Loop(base.BaseAction):
    cmd = 'loop'
    args = ['int']

    def __init__(self, configuration):
        super(Loop, self).__init__(configuration)

    def run(self, n, **configuration):
        LOG.debug('would loop: %d times' % n)
