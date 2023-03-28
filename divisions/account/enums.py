import enum


class AccountTransactionType(enum.Enum):
    DEPOSIT = 1
    WITHDRAWAL = 2


class AccountTransactionStatus(enum.Enum):
    INITIATED = 1
    PENDING_CONFIRMATION = 2
    SUCCESS = 3
    FAILED = 4
    IN_PROCESS = 5
    CONFIRMED = 6
    CANCELED = 7


class AccountWalletBalanceType(enum.Enum):
    INVESTMENT = 1
