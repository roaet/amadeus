import hashlib
import logging

import numpy as np
import pandas as pd
import yaml
from ruamel import yaml

from amadeus import constants
from amadeus import utils
from amadeus import yaml_object as yo


LOG = logging.getLogger(__name__)

TOP_LEVEL_KEY = 'composition'


class BaseComposition(yo.YAMLBackedObject):
    def __init__(self, yaml_file, conf):
        """Assumes that yaml_file is valid."""
        super(BaseComposition, self).__init__(yaml_file, conf, TOP_LEVEL_KEY)

    def __repr__(self):
        return "COMP(%s:%s)" % (self.type, self.filename)

    @staticmethod
    def check(yaml_obj, yaml_file):
        return yo.YAMLBackedObject.check(
            yaml_obj, yaml_file, TOP_LEVEL_KEY, constants.COMPOSITION_TYPES)
