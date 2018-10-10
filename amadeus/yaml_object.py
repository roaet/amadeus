import logging

from ruamel import yaml

from amadeus import utils


LOG = logging.getLogger(__name__)

class YAMLBackedObject(object):
    def __init__(self, yaml_file, conf, key):
        """Assumes that yaml_file is valid."""
        self.yaml_file = yaml_file
        self.filename = utils.basename(self.yaml_file)
        self.conf = conf
        with open(yaml_file, 'r') as stream:
            self.original_yaml_obj = yaml.safe_load(stream)
        self.yaml_obj = self.original_yaml_obj[key]
        self.type = self.yaml_obj['type']

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
        yo_type = yaml_obj[key]['type']
        if yo_type not in types:
            LOG.warning("%s not a known %s type from %s" %
                (yo_type, key, yaml_file))
            return False
        return True
