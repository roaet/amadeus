import logging

from amadeus.actions.basic import base_action as base


LOG = logging.getLogger(__name__)


class Print(base.BaseAction):
    cmd = 'print'
    args = ['str']

    def __init__(self, conf):
        super(Print, self).__init__(conf)

    def run(self, message, **conf):
        LOG.info('AMADEUS: %s' % message)
