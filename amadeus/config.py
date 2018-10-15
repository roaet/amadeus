import sys

from configobj import ConfigObj
from amadeus import constants
from amadeus import exceptions as exc
from amadeus import utils


class Configuration(object):
    def __init__(self):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self._check_directory_sanity()
        self._configure()

    @property
    def config(self):
        return self._conf

    def _check_directory_sanity(self):
        checks = [
            constants.USER_HOME_DIR,
            constants.CACHE_DIR,
            constants.TEST_DATA_DIR,
            constants.DEFAULT_RESOURCE_DIR,
            constants.DEFAULT_DATASOURCE_DIR,
            constants.DEFAULT_COMPOSITION_DIR,
        ]
        for directory in checks:
            if not utils.does_directory_exist(directory):
                utils.make_directory(directory)

    def _get_directory_info(self):
        return [
            "Directory Information:",
            "Project root: %s" % constants.PROJECT_ROOT,
            "Support files: %s" % constants.DEFAULT_SUPPORT_DIR,
            "Training files: %s" % constants.DEFAULT_TRAINING_DIR,
            "Resource directory: %s" % constants.DEFAULT_RESOURCE_DIR,
            "Datasource directory: %s" % constants.DEFAULT_DATASOURCE_DIR,
            "Composition directory: %s" % constants.DEFAULT_COMPOSITION_DIR,
            "User Home directory: %s" % constants.USER_HOME_DIR,
            "Default configuration: %s" % constants.DEFAULT_CONF_DIRS,
            "Cache directory: %s" % constants.CACHE_DIR,
            "Test Data directory: %s" % constants.TEST_DATA_DIR,
            "Default Log location: %s" % constants.LOG_LOCATION,
            "Current Config: %s" % self.config_path,
        ]

    def _configure(self):
        found_config = None
        for path in constants.DEFAULT_CONF_DIRS:
            if utils.does_file_exist(path):
                found_config = path
                break

        if found_config is None:
            locations = ", ".join(constants.DEFAULT_CONF_DIRS)
            raise exc.ConfigError(
                'Config not found in expected locations: %s' % locations)
        conf = ConfigObj(found_config)
        self.config_path = found_config
        self._conf = conf
        self._get_directory_info()
