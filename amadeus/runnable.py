import logging

import click

from amadeus.config import Configuration
from amadeus.datasources import factory
from amadeus.datasources import loader
from amadeus.logger import Logger
from amadeus.connections import manager
from amadeus import utils


LOG = logging.getLogger(__name__)


class Runnable(object):
    def __init__(self, debug):
        self.conf = Configuration().config
        Logger(self.conf, debug).configure()


def parse_configurations(confs):
    out = {}
    for conf in confs:
        key, val = conf.split('=')
        out[key] = val
    return out
