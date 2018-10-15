import importlib
import inspect
import logging
import pkgutil

from amadeus import constants
from amadeus import actions as acts
from amadeus.actions.basic import base_action


LOG = logging.getLogger(__name__)


class ActionFactory(object):
    def __init__(self, configuration):
        self.actions = {}
        self.conf = configuration
        self._define_actions()

    def has_action(self, action_name):
        return action_name in self.actions

    def get_action(self, action_name):
        if action_name not in self.actions:
            return None
        return self.actions[action_name]

    def _define_actions(self):
        LOG.debug(
            "Search root starting at: %s" % constants.ACTION_ROOT_SEARCH_DIR)
        res = self._import_submodules(acts)
        for name, mod in res.iteritems():
            clsmembers = inspect.getmembers(mod, inspect.isclass)
            for name, cls in clsmembers:
                if issubclass(
                        cls, base_action.BaseAction) and hasattr(cls, 'cmd'):
                    LOG.debug("Found valid action: %s (%s)" % (cls.cmd, name))
                    self.actions[cls.cmd] = cls

    def _import_submodules(self, package, recursive=True):
        if isinstance(package, str):
            package = importlib.import_module(package)
        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + '.' + name
            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(self._import_submodules(full_name))
        return results

    def __call__(self, action, *args, **kwargs):
        if action not in self.actions:
            return None
        Action = self.actions[action]
        inst = Action(self.conf)
        if len(args) < len(Action.args):
            LOG.debug("Incorrect arg count")
            return None
        inst.run(*args, **kwargs)
