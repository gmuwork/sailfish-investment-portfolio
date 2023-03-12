import typing


def get_exception_message(exception: Exception) -> str:
    if isinstance(exception, type):
        return exception.__name__

    if hasattr(exception, "message") and exception.message:
        return exception.message
    return exception.args[0] if len(exception.args) else ""


def convert_timestamp_to_milliseconds(timestamp: typing.Union[int, float]) -> int:
    return timestamp * 10 ** 3
