import logging


FORMAT = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] "
    "%(message)s")


class Logger(object):
    def __init__(self, conf, debug=False, verbosity=0):
        self.conf = conf
        self.debug = debug
        self.verbosity = verbosity
        self.format = conf.get('log_format', FORMAT)

    def configure(self):
        level = logging.WARNING
        if self.conf.get('log_level') == 'DEBUG':
            level = logging.DEBUG
        if self.conf.get('log_level') == 'INFO':
            level = logging.INFO

        if self.verbosity == 1:
            level = logging.INFO
        if self.verbosity >= 2:
            level = logging.DEBUG

        if self.debug:
            level = logging.DEBUG

        logging.basicConfig(format=FORMAT)
        log_format = logging.Formatter(FORMAT)
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.setLevel(level)
        # file_handler = logging.FileHandler(constants.LOG_LOCATION)
        # file_handler.setFormatter(log_format)
        # root_logger.addHandler(file_handler)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(log_format)
        root_logger.addHandler(ch)
