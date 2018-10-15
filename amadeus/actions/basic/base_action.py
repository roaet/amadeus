import logging


LOG = logging.getLogger(__name__)


class BaseAction(object):
    args = []

    def __init__(self, conf):
        self.conf = conf
        self.cmd = ''

    def run(self, **conf):
        returns = conf.get('returns', None)
        if 'returns' in conf:
            del conf['returns']
        LOG.debug("Returns are: %s" % returns)
