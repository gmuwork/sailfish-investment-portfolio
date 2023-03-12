import enum
import typing


class CryptoProvider(enum.Enum):
    BYBIT = "BYBIT"

    def to_integer_choice(self) -> int:
        return {CryptoProvider.BYBIT: 1}[self]

    @staticmethod
    def from_integer_choice(choice: int) -> enum.Enum:
        return {1: CryptoProvider.BYBIT}[choice]


class TradingSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"
