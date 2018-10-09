class AmadeusException(Exception):
    pass


class ConfigError(AmadeusException):
    pass


class ConnectionFailed(AmadeusException):
    pass
