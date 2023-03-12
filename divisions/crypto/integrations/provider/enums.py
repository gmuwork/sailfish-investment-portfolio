import enum


class TradingCategory(enum.Enum):
    SPOT = "spot"
    OPTION = "option"
    LINEAR = "linear"
    inverse = "inverse"
