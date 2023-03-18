import datetime
import decimal
import typing

from divisions.crypto import enums as crypto_enums
from divisions.crypto.integrations.provider import enums


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


class TradeOrder(
    typing.NamedTuple(
        "TradeOrder",
        [
            ("market_instrument_name", str),
            ("order_id", str),
            ("order_side", str),
            ("order_quantity", decimal.Decimal),
            ("order_price", decimal.Decimal),
            ("average_order_price", decimal.Decimal),
            ("order_type", str),
            ("order_status", str),
            ("order_total_executed_value", decimal.Decimal),
            ("order_total_executed_quantity", decimal.Decimal),
            ("order_total_executed_fee", decimal.Decimal),
            ("created_at", datetime.datetime),
            ("updated_at", datetime.datetime),
        ],
    )
):
    __slots__ = ()


TradeOrder.__new__.__defaults__ = (None,) * len(TradeOrder._fields)


class TradeExecution(
    typing.NamedTuple(
        "TradeExecution",
        [
            ("market_instrument_name", str),
            ("order_id", typing.Optional[str]),
            ("execution_id", str),
            ("execution_side", str),
            ("executed_fee", decimal.Decimal),
            ("execution_price", decimal.Decimal),
            ("execution_quantity", decimal.Decimal),
            ("execution_type", str),
            ("execution_value", decimal.Decimal),
            ("is_maker", bool),
            ("created_at", datetime.datetime),
        ],
    )
):
    __slots__ = ()


TradeExecution.__new__.__defaults__ = (None,) * len(TradeExecution._fields)


class WalletBalance(
    typing.NamedTuple(
        "WalletBalance",
        [
            ("currency_name", str),
            ("amount", decimal.Decimal),
        ],
    )
):
    __slots__ = ()


WalletBalance.__new__.__defaults__ = (None,) * len(WalletBalance._fields)
