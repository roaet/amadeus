from amadeus import constants
from amadeus.playbooks import base


class PlaybookFactory(object):
    def __init__(self, conf):
        self.conf = conf

    def get_type(
            self, pb_type):
        if pb_type == constants.PB_BASE:
            return base.BasePlaybook
        return None

    def create(self, pb_type, yamlfile):
        pb = None
        if pb_type == constants.PB_BASE:
            return base.BasePlaybook(yamlfile, self.conf)
        return pb


