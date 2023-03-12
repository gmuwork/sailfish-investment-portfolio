import enum


class SignatureType(enum.Enum):
    RSA = 1
    HMAC = 2


class TradingCategory(enum.Enum):
    SPOT = "spot"
    OPTION = "option"
    LINEAR = "linear"
    inverse = "inverse"
