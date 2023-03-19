import enum
import typing


class HttpMethod(enum.Enum):
    GET = "get"
    POST = "post"


class Currency(enum.Enum):
    USDT = "USDT"
    ETH = "ETH"
