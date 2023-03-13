import datetime
import decimal
import typing

from backend.divisions.crypto import enums as crypto_enums
from backend.divisions.crypto.integrations.provider import enums

class MarketInstrument(
    typing.NamedTuple(
        "MarketInstrument",
        [
            ("name", str),
            ("status", str),
        ],
    )
):
    __slots__ = ()


MarketInstrument.__new__.__defaults__ = (None,) * len(MarketInstrument._fields)


class TradePosition(
    typing.NamedTuple(
        "TradePosition",
        [
            ("market_instrument_name", str),
            ("position_side", str),
            ("position_size", decimal.Decimal),
            ("position_value", decimal.Decimal),
            ("entry_price", decimal.Decimal),
            ("created_at", datetime.datetime),
            ("updated_at", datetime.datetime),
        ],
    )
):
    __slots__ = ()


TradePosition.__new__.__defaults__ = (None,) * len(TradePosition._fields)


class TradePnLPosition(
    typing.NamedTuple(
        "TradePnLPosition",
        [
            ("market_instrument_name", str),
            ("order_id", str),
            ("position_side", str),
            ("position_quantity", decimal.Decimal),
            ("order_price", decimal.Decimal),
            ("order_type", str),
            ("position_closed_size", decimal.Decimal),
            ("total_entry_value", decimal.Decimal),
            ("average_entry_price", decimal.Decimal),
            ("total_exit_value", decimal.Decimal),
            ("average_exit_price", decimal.Decimal),
            ("closed_pnl", decimal.Decimal),
            ("created_at", datetime.datetime),
        ],
    )
):
    __slots__ = ()


TradePnLPosition.__new__.__defaults__ = (None,) * len(TradePnLPosition._fields)


class TradePositionPerformance(
    typing.NamedTuple(
        "TradePositionPerformance",
        [
            ("market_instrument_name", str),
            ("provider", crypto_enums.CryptoProvider),
            ("trading_category", enums.TradingCategory),
            ("year", typing.Optional[int]),
            ("month", typing.Optional[int]),
            ("week", typing.Optional[int]),
            ("day", typing.Optional[int]),
            ("pnl", decimal.Decimal),
        ],
    )
):
    __slots__ = ()


TradePositionPerformance.__new__.__defaults__ = (None,) * len(
    TradePositionPerformance._fields
)
