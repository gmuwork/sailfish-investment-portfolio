import enum
import typing

from divisions.blockchain.integrations.clients.bybit import enums as bybit_enums
from divisions.crypto import enums as crypto_enums


class TradingCategory(enum.Enum):
    SPOT = "spot"
    OPTION = "option"
    LINEAR = "linear"
    INVERSE = "inverse"

    def convert_to_internal(
        self, provider: crypto_enums.CryptoProvider
    ) -> bybit_enums.TradingCategory:
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

    def convert_to_internal(
        self, provider: crypto_enums.CryptoProvider
    ) -> bybit_enums.TradeOrderStatus:
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

    def convert_to_internal(
        self, provider: crypto_enums.CryptoProvider
    ) -> bybit_enums.TradeExecutionType:
        return {
            crypto_enums.CryptoProvider.BYBIT: {
                self.TRADE: bybit_enums.TradeExecutionType.TRADE,
                self.FUNDING: bybit_enums.TradeExecutionType.FUNDING,
                self.ADL_TRADE: bybit_enums.TradeExecutionType.ADL_TRADE,
                self.BUST_TRADE: bybit_enums.TradeExecutionType.BUST_TRADE,
                self.SETTLE: bybit_enums.TradeExecutionType.SETTLE,
            }
        }[provider][self]


class WalletType(enum.Enum):
    DERIVATIVE = "DERIVATIVE"
    SPOT = "SPOT"
    INVESTMENT = "INVESTMENT"
    OPTION = "OPTION"
    GENERAL = "GENERAL"
    FUND = "FUND"

    def convert_to_internal(
        self, provider: crypto_enums.CryptoProvider
    ) -> bybit_enums.AccountType:
        return {
            crypto_enums.CryptoProvider.BYBIT: {
                self.DERIVATIVE: bybit_enums.AccountType.CONTRACT,
            }
        }[provider][self]

    @staticmethod
    def convert_from_internal(
        wallet_type: typing.Union[bybit_enums.AccountType],
    ) -> "WalletType":
        return {
            bybit_enums.AccountType.CONTRACT: WalletType.DERIVATIVE,
            bybit_enums.AccountType.SPOT: WalletType.SPOT,
            bybit_enums.AccountType.INVESTMENT: WalletType.INVESTMENT,
            bybit_enums.AccountType.OPTION: WalletType.OPTION,
            bybit_enums.AccountType.UNIFIED: WalletType.GENERAL,
            bybit_enums.AccountType.FUND: WalletType.FUND,
        }[wallet_type]


class WalletTransferStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"

    @staticmethod
    def convert_from_internal(
        status: typing.Union[bybit_enums.WalletInternalTransferStatus],
    ) -> "WalletTransferStatus":
        return {
            bybit_enums.WalletInternalTransferStatus.SUCCESS: WalletTransferStatus.SUCCESS,
            bybit_enums.WalletInternalTransferStatus.FAILED: WalletTransferStatus.FAILED,
            bybit_enums.WalletInternalTransferStatus.PENDING: WalletTransferStatus.PENDING,
        }[status]


class WalletTransferType(enum.Enum):
    INTERNAL_DEPOSIT = "INTERNAL_DEPOSIT"
    INTERNAL_WITHDRAWAL = "INTERNAL_WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    COMMISSION = "COMMISSION"


class PortfolioAccountType(enum.Enum):
    MANAGER = "MANAGER"
    INVESTOR = "INVESTOR"


class PortfolioAccountStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
