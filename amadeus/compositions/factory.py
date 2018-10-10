from amadeus import constants
from amadeus.compositions import base


class CompositionFactory(object):
    def __init__(self, conf):
        self.conf = conf

    def get_type(
            self, comp_type):
        if comp_type == constants.COMP_BASE:
            return base.BaseComposition
        return None

    def create(self, comp_type, yaml_obj):
        comp = None
        if comp_type == constants.COMP_BASE:
            return base.BaseComposition(yaml_obj, self.conf)
        return comp
