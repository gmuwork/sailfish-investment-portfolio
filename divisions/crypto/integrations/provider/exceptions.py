class ProviderError(Exception):
    pass


class APIClientError(ProviderError):
    pass


class NoEligibleProviderFoundError(ProviderError):
    pass


class DataValidationError(ProviderError):
    pass


class TradingCategoryNotSupportedError(ProviderError):
    pass
