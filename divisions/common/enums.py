import enum
import typing


class HttpMethod(enum.Enum):
    GET = "get"
    POST = "post"


class Currency(enum.Enum):
    USDT = "USDT"
    ETH = "ETH"

    def to_integer_choice(self) -> int:
        return {
            Currency.USDT: 1,
            Currency.ETH: 2,
        }[self]
