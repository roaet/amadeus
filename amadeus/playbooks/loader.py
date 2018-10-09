import logging

from amadeus import constants
from amadeus.playbooks.base import BasePlaybook
from amadeus import yaml_loader


LOG = logging.getLogger(__name__)


class PlaybookLoader(object):
    def __init__(self, conf, factory):
        self.loader = yaml_loader.YAMLLoader(
            conf, factory, constants.DEFAULT_PLAYBOOK_DIR,
            BasePlaybook, 'playbook')

    def has_playbook(self, playbook_name):
        return self.loader.has_entity(playbook_name)

    def load_playbook(self, playbook_name):
        return self.loader.load_entity(playbook_name)
