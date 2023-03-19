import logging
import typing

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from divisions.common import enums as common_enums
from divisions.common import utils as common_utils
from divisions.crypto import enums as crypto_enums
from divisions.crypto.integrations.provider import factory as crypto_provider_factory
from divisions.crypto.integrations.provider import (
    exceptions as crypto_provider_exceptions,
)
from divisions.crypto.integrations.provider import enums as crypto_provider_enums
from divisions.crypto.integrations.provider.services import (
    data_importer as data_importer_services,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Imports wallet balances data.
            ex. python manage.py import_wallet_balances --provider=BYBIT --wallet-type=DERIVATIVE --currency=USDT
            """

    def add_arguments(self, parser):
        parser.add_argument(
            "--provider",
            help="Provider for which wallet balance are to be imported. One of CryptoProvider enum choices.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--wallet-type",
            help="Wallet type for which wallet balance is to be imported. One of WalletType enum choices.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--currency",
            help="Currency for which wallet balance is to be imported. One of WalletType enum choices.",
            required=True,
            type=str,
        )

    provider = None
    wallet_type = None
    currency = None

    log_prefix = "[IMPORT-WALLET-BALANCES]"

    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._setup_config_variables(kwargs=kwargs)
        logger.info(
            "{} Started command '{}' (provider={}, currency={}, wallet_type={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                self.provider.name,
                self.currency.name,
                self.wallet_type.name,
            )
        )

        try:
            data_importer_services.CryptoProviderImporter(
                provider_client=crypto_provider_factory.Factory(
                    provider=self.provider
                ).create()
            ).import_wallet_balances(
                wallet_type=self.wallet_type, currency=self.currency
            )
        except crypto_provider_exceptions.NoEligibleProviderFoundError:
            msg = "Unable to create provider client (provider={})".format(
                self.provider.name
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise CommandError(msg)
        except crypto_provider_exceptions.ProviderError as e:
            msg = "Unable to import wallet balances (currency={}, wallet_type={}). Error: {}".format(
                self.currency.name,
                self.wallet_type.name,
                common_utils.get_exception_message(exception=e),
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise CommandError(msg)
        except Exception as e:
            msg = "Unexpected exception occurred while importing wallet balances. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise CommandError(msg)

        logger.info(
            "{} Finished command '{}' (provider={}, currency={}, wallet_type={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                self.provider.name,
                self.currency.name,
                self.wallet_type.name,
            )
        )

    def _setup_config_variables(self, kwargs: typing.Dict) -> None:
        try:
            self.provider = crypto_enums.CryptoProvider(kwargs["provider"])
            self.wallet_type = crypto_provider_enums.WalletType(kwargs["wallet_type"])
            self.currency = common_enums.Currency(kwargs["currency"])
        except Exception as e:
            msg = "Unable to setup config variables. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}. Exiting.".format(self.log_prefix, msg))
            raise CommandError(msg)
