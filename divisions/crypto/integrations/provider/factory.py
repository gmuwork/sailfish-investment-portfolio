import logging

from backend.divisions.crypto import enums as crypto_enums
from backend.divisions.crypto.integrations.provider import base as base_client
from backend.divisions.crypto.integrations.provider import exceptions
from backend.divisions.crypto.integrations.provider.bybit import client as bybit_client

_LOG_PREFIX = "[PROVIDER-CLIENT-FACTORY]"
logger = logging.getLogger(__name__)


class Factory(object):
    PROVIDER_CLIENT_MAP = {
        crypto_enums.CryptoProvider.BYBIT: bybit_client.ByBitProvider
    }

    def __init__(self, provider: crypto_enums.CryptoProvider) -> None:
        self.provider = provider

    def create(self) -> base_client.BaseProvider:
        provider = self.PROVIDER_CLIENT_MAP.get(self.provider)
        if not provider:
            msg = "No eligible crypto provider client (provider={})".format(
                self.provider.name
            )
            logger.error("{} {}.".format(_LOG_PREFIX, msg))
            raise exceptions.NoEligibleProviderFoundError(msg)

        return provider()
