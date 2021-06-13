
class ConfigNotFound(Exception):
    def __init__(self, message):
        if not message:
            message = 'Config file not found'
        super(ConfigNotFound, self).__init__(message)
