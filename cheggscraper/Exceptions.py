class FailedToParse(Exception):
    def __init__(self):
        self.message = 'Failed to parse data'


class UnableToParseUUID(FailedToParse):
    def __init__(self):
        self.message = 'Unable to get question uuid'


class UnexpectedStatusCode(Exception):
    def __init__(self, status_code: int):
        self.message = 'Unexpected status code: {}'.format(status_code)


class UnableToGetLegacyQuestionID(FailedToParse):
    def __init__(self):
        self.message = 'Unable to get question legacy id'


class FailedToParseAnswer(FailedToParse):
    def __init__(self):
        self.message = 'Failed to parse answer'


class JsonParseError(Exception):
    ...


class UnableToGetToken(FailedToParse):
    def __init__(self):
        self.message = 'Unable to get token'


class UrlNotSupported(ValueError):
    def __init__(self, url):
        self.message = f'URL NOT SUPPORTED: {url}'


class CookieFileDoesNotExist(FileNotFoundError):
    def __init__(self, path):
        self.message = f'File does not exist: {path}'


class BotFlagError(Exception):
    def __init__(self):
        self.message = 'The account is flagged as bot, open you chegg account with same browser where you get the cookies and fill the captcha'
