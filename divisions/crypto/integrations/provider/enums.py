import enum


class TradingCategory(enum.Enum):
    SPOT = "spot"
    OPTION = "option"
    LINEAR = "linear"
    inverse = "inverse"


# TODO: Create internal and create conversions to internal
class TradeOrderStatus(enum.Enum):
    CREATED = "Created"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"
    FILLED = "Filled"


class TradeExecutionType(enum.Enum):
    TRADE = "Trade"
    FUNDING = "Funding"
    ADL_TRADE = "AdlTrade"
    BUST_TRADE = "BustTrade"
    SETTLE = "Settle"
