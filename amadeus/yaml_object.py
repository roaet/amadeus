import logging

from ruamel import yaml

from amadeus import utils


LOG = logging.getLogger(__name__)

class YAMLBackedObject(object):
    def __init__(self, yaml_obj, conf, key):
        self.conf = conf
        self.original_yaml_obj = yaml_obj
        self.yaml_obj = self.original_yaml_obj[key]
        self.type = self.yaml_obj['type']
        self.name = self.yaml_obj['name']

    @property
    def yamldump(self):
        return "---\n" + yaml.dump(
            self.original_yaml_obj, Dumper=yaml.RoundTripDumper)

    @staticmethod
    def check(yaml_obj, yaml_file, key, types):
        if key not in yaml_obj:
            LOG.warning(
                "Missing required '%s' top-level key "
                "of file %s" % (key, yaml_file))
            return False
        if 'type' not in yaml_obj[key]:
            LOG.warning(
                "Missing required 'type' 2nd-level key of file %s" %
                yaml_file)
            return False
        if 'name' not in yaml_obj[key]:
            LOG.warning(
                "Missing required 'name' 2nd-level key of file %s" %
                yaml_file)
            return False
        yo_type = yaml_obj[key]['type']
        if yo_type not in types:
            LOG.warning("%s not a known %s type from %s" %
                (yo_type, key, yaml_file))
            return False
        return True
