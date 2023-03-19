import decimal

from divisions.crypto import enums as crypto_enums
from divisions.crypto.integrations.provider import enums as provider_enums


def calculate_portfolio_investor_participation(
    portfolio_user_id: int,
    portfolio_type: provider_enums.WalletType,
    provider: crypto_enums.CryptoProvider,
) -> decimal.Decimal:
    pass
