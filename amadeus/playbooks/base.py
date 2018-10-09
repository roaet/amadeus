import hashlib
import logging

import numpy as np
import pandas as pd
import yaml

from amadeus import constants
from amadeus import utils


LOG = logging.getLogger(__name__)


class BasePlaybook(object):
    def __init__(self, yaml_file, conf):
        """Assumes that yaml_file is valid."""
        self.yaml_file = yaml_file
        self.filename = utils.basename(self.yaml_file)
        self.conf = conf
        with open(yaml_file, 'r') as stream:
            self.yaml_obj = yaml.load(stream)['playbook']
        self.type = self.yaml_obj['type']

    def __repr__(self):
        return "PB(%s:%s)" % (self.type, self.filename)

    @staticmethod
    def check(yaml_obj):
        if 'playbook' not in yaml_obj:
            LOG.warning(
                "Missing required 'playbook' top-level key "
                "of file %s" % yaml_file)
            return False
        if 'type' not in yaml_obj['playbook']:
            LOG.warning(
                "Missing required 'type' 2nd-level key of file %s" %
                yaml_file)
            return False
        return True
