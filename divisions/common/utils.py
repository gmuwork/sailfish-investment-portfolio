import typing

from divisions.common import constants
from divisions.common import enums


def get_exception_message(exception: Exception) -> str:
    if isinstance(exception, type):
        return exception.__name__

    if hasattr(exception, "message") and exception.message:
        return exception.message
    return exception.args[0] if len(exception.args) else ""


def convert_timestamp_to_milliseconds(timestamp: typing.Union[int, float]) -> int:
    return int(timestamp * 10 ** 3)


def get_chain_currency(currency: enums.Currency) -> enums.Currency:
    return constants.TRANSACTION_CHAIN_CURRENCY_MAP[currency]
