import enum


class SignatureType(enum.Enum):
    RSA = 1
    HMAC = 2


class TradingCategory(enum.Enum):
    SPOT = "spot"
    OPTION = "option"
    LINEAR = "linear"
    INVERSE = "inverse"


class TradeOrderStatus(enum.Enum):
    CREATED = "Created"
    NEW = "New"
    REJECTED = "Rejected"
    PARTIALLY_FILLED = "PartiallyFilled"
    PARTIALLY_FILLED_CANCELLED = "PartiallyFilledCanceled"
    FILLED = "Filled"
    CANCELLED = "Cancelled"
    UNTRIGGERED = "Untriggered"
    TRIGGERED = "Triggered"
    DEACTIVATED = "Deactivated"


class TradeExecutionType(enum.Enum):
    TRADE = "Trade"
    FUNDING = "Funding"
    ADL_TRADE = "AdlTrade"
    SETTLE = "Settle"
    BUST_TRADE = "BustTrade"


class StatusCode(enum.Enum):
    OK = 0


class AccountType(enum.Enum):
    CONTRACT = "CONTRACT"
    SPOT = "SPOT"
    INVESTMENT = "INVESTMENT"
    OPTION = "OPTION"
    UNIFIED = "UNIFIED"
    FUND = "FUND"


class WithdrawalType(enum.Enum):
    ON_CHAIN = 0
    OFF_CHAIN = 1
    ALL = 2


class WalletInternalTransferStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"
