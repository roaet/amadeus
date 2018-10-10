import logging

from amadeus import constants
from amadeus.compositions.base import BaseComposition
from amadeus import yaml_loader


LOG = logging.getLogger(__name__)


class CompositionLoader(object):
    def __init__(self, conf, factory):
        self.loader = yaml_loader.YAMLLoader(
            conf, factory, constants.DEFAULT_COMPOSITION_DIR,
            BaseComposition, 'composition')

    def has_composition(self, comp_name):
        return self.loader.has_entity(comp_name)

    def load_composition(self, comp_name):
        return self.loader.load_entity(comp_name)

    def load_composition_str(self, comp_str):
        return self.loader.load_entity_with_yaml_str(comp_str)
