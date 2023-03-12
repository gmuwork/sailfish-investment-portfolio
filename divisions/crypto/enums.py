import enum


class CryptoProvider(enum.Enum):
    BYBIT = "BYBIT"


class TradingSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"
