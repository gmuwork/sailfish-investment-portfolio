import enum
import typing

from backend.divisions.blockchain.integrations.clients.bybit import enums as bybit_enums
from backend.divisions.crypto import enums as crypto_enums


class TradingCategory(enum.Enum):
    SPOT = "spot"
    OPTION = "option"
    LINEAR = "linear"
    INVERSE = "inverse"

    def convert_to_internal(self, provider: crypto_enums.CryptoProvider) -> 'TradingCategory':
        return {
            crypto_enums.CryptoProvider.BYBIT: {
                self.SPOT: bybit_enums.TradingCategory.SPOT,
                self.OPTION: bybit_enums.TradingCategory.OPTION,
                self.LINEAR: bybit_enums.TradingCategory.LINEAR,
                self.INVERSE: bybit_enums.TradingCategory.INVERSE,
            }
        }[provider][self]


class TradeOrderStatus(enum.Enum):
    CREATED = "created"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FILLED = "filled"

    def convert_to_internal(self, provider: crypto_enums.CryptoProvider) -> 'TradeOrderStatus':
        return {
            crypto_enums.CryptoProvider.BYBIT: {
                self.CREATED: bybit_enums.TradeOrderStatus.CREATED,
                self.REJECTED: bybit_enums.TradeOrderStatus.REJECTED,
                self.CANCELLED: bybit_enums.TradeOrderStatus.CANCELLED,
                self.FILLED: bybit_enums.TradeOrderStatus.FILLED,
            }
        }[provider][self]


class TradeExecutionType(enum.Enum):
    TRADE = "trade"
    FUNDING = "funding"
    ADL_TRADE = "adl_trade"
    BUST_TRADE = "bust_trade"
    SETTLE = "settle"

    def convert_to_internal(self, provider: crypto_enums.CryptoProvider) -> 'TradeExecutionType':
        return {
            crypto_enums.CryptoProvider.BYBIT: {
                self.TRADE: bybit_enums.TradeExecutionType.TRADE,
                self.FUNDING: bybit_enums.TradeExecutionType.FUNDING,
                self.ADL_TRADE: bybit_enums.TradeExecutionType.ADL_TRADE,
                self.BUST_TRADE: bybit_enums.TradeExecutionType.BUST_TRADE,
                self.SETTLE: bybit_enums.TradeExecutionType.SETTLE,
            }
        }[provider][self]
