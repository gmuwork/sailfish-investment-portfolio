import datetime
import decimal
import typing


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


class DerivativePosition(
    typing.NamedTuple(
        "DerivativePosition",
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


DerivativePosition.__new__.__defaults__ = (None,) * len(DerivativePosition._fields)


class DerivativePnLPosition(
    typing.NamedTuple(
        "DerivativePnLPosition",
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


DerivativePnLPosition.__new__.__defaults__ = (None,) * len(
    DerivativePnLPosition._fields
)
