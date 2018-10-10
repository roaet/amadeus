import logging

from ruamel import yaml
from yamllint import config
from yamllint import linter

from amadeus import constants
from amadeus.datasources.base import BaseDatasource
from amadeus import utils


LOG = logging.getLogger(__name__)


class YAMLLoader(object):
    def __init__(self, conf, factory, base_dir, base_class, base_key):
        self.base_dir = base_dir
        self.files = self._get_entities_from_resource_dir()
        self.conf = conf
        self.factory = factory
        self.base_object_class = base_class
        self.base_key = base_key

    def _get_entities_from_resource_dir(self):
        resource_dir = self.base_dir
        files = utils.glob_files(resource_dir, '*.yaml')
        return files

    def _is_entity_in_files(self, entity_name, files):
        for f in files:
            if ('%s.yaml' % entity_name) == utils.basename(f):
                return True
        return False

    def _get_entity_file(self, entity_name, files):
        for f in files:
            if ('%s.yaml' % entity_name) == utils.basename(f):
                return f
        return None

    def get_type_from_yaml(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            yaml_obj = yaml.safe_load(stream)
            return yaml_obj[self.base_key]['type']

    def _does_yaml_lint(self, yaml_file):
        conf = utils.path_join(
            constants.DEFAULT_BASE_CONF, 'default_yaml_lint.yaml')
        yaml_conf = config.YamlLintConfig(file=conf)

        with open(yaml_file, 'r') as stream:
            lint_problems = linter.run(stream, yaml_conf)

        problems = 0
        for problem in lint_problems:
            LOG.warning(problem)
            problems += 1
        if problems > 0:
            LOG.warning("%d problems detected with YAML (%s)" % (
                problems, yaml_file))
            return False
        return True

    def _does_yaml_exist(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            yaml_obj = yaml.safe_load(stream)
            if yaml_obj is None:
                LOG.warning("YAML object was None after load of file %s" %
                    (yaml_file))
                return False
        return True

    def _does_yaml_have_basic_keys(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            yaml_obj = yaml.safe_load(stream)
        if not self.base_object_class.check(
                yaml_obj, yaml_file, self.base_key):
            LOG.warning("%s failed basic check" % yaml_file)
            return False
        return True

    def _is_yaml_valid_for_type(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            yaml_obj = yaml.safe_load(stream)
        ent_type = yaml_obj[self.base_key]['type']
        ent_class = self.factory.get_type(ent_type)
        if not ent_class.check(yaml_obj, yaml_file):
            LOG.warning("%s failed %s check" % (
                yaml_file, ent_class.__name__))
            return False
        return True

    def is_yaml_valid(self, yaml_file):
        if not utils.does_file_exist(yaml_file):
            LOG.warning("%s is not a file" % yaml_file)
            return False
        try:
            if not self._does_yaml_lint(yaml_file):
                LOG.error("%s failed to validate" % yaml_file)
                return False
            if not self._does_yaml_exist(yaml_file):
                LOG.error("%s did not produce yaml object" % yaml_file)
                return False
            if not self._does_yaml_have_basic_keys(yaml_file):
                LOG.error("%s did not have basic keys" % yaml_file)
                return False
            if not self._is_yaml_valid_for_type(yaml_file):
                LOG.error("%s was not valid for type" % yaml_file)
                return False
        except yaml.YAMLError, e:
            LOG.error("Error while parsing YAML (%s): %s" % (
                yaml_file, e))
            return False
        return True

    def has_entity(self, entity_name):
        return self._is_entity_in_files(entity_name, self.files)

    def load_entity(self, entity_name):
        entity_file = self._get_entity_file(
            entity_name, self.files)
        if not self.is_yaml_valid(entity_file):
            LOG.error("YAML file (%s) for %s is invalid" % (
                entity_file, entity_name))
            return None
        ent_type = self.get_type_from_yaml(entity_file)
        with open(entity_file, 'r') as stream:
            yaml_obj = yaml.safe_load(stream)
        ent = self.factory.create(ent_type, yaml_obj)
        return ent

    def load_entity_with_yaml_str(self, yaml_str):
        return self.load_entity_with_yaml_obj(yaml.safe_load(yaml_str))

    def load_entity_with_yaml_obj(self, yaml_obj):
        ent_type = yaml_obj[self.base_key]['type']
        ent = self.factory.create(ent_type, yaml_obj)
        return ent
