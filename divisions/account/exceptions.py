class AccountServiceException(Exception):
    pass


class UserAlreadyExists(AccountServiceException):
    pass


class UserInvalidPasswordError(AccountServiceException):
    pass
