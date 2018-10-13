import logging


LOG = logging.getLogger(__name__)

class BaseAction(object):
    args = []
    def __init__(self, configuration):
        self.conf = configuration
        self.cmd = ''
