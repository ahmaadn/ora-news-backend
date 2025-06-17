from enum import StrEnum, auto


class ErrorCode(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.upper()

    APP_ERROR = auto()
    INVALID_USERNAME = auto()
    INVALID_EMAIL = auto()
    INVALID_PASSOWRD = auto()
    INVALID_USER_UUID = auto()
    INVALID_TOKEN_CREDENTIALS = auto()
    INVALID_TOKEN = auto()
    INVALID_RESET_PASSOWORD_TOKEN = auto()
    INVALID_TOKEN_VERIFY = auto()
    INVALID_LOGIN_CREDENTIALS = auto()

    USER_ID_INVALID = auto()
    USER_EMAIL_ALREADY_USED = auto()
    USERNAME_ALREADY_USED = auto()
    USER_ALREADY_EXISTS = auto()
    USER_ALREADY_VERIFIED = auto()
    USER_NOT_VERIFIED = auto()
    USER_NOT_EXISTS = auto()
    USER_NOT_ACTIVE = auto()
    USER_ID_NOTFOUND = auto()
    USER_NOT_HAVE_PERMISSION = auto()

    NOT_AUTHENTICATED = auto()
