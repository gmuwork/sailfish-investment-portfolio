import datetime
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
            Imports account transfer data.
            ex. python manage.py import account transfers --provider=BYBIT --wallet-type=DERIVATIVE --currency=USDT --depth=1 --from-datetime=2022-01-01 --to-datetime=2023-01-01 [--dry-run]
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
        parser.add_argument(
            "--from-datetime",
            help="From which datetime trading data is to be imported. One of TradingCategory enum choices.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--to-datetime",
            help="To which datetime trading data is to be imported. One of TradingCategory enum choices.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--dry-run",
            help="Runs command in dry run mode",
            action="store_true",
            default=False,
        )

    provider = None
    wallet_type = None
    currency = None
    from_datetime = None
    to_datetime = None
    dry_run = None

    log_prefix = "[IMPORT-ACCOUNT-TRANSFERS]"

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
            ).import_wallet_internal_transfers(
                wallet_type=self.wallet_type,
                currency=self.currency,
                from_datetime=self.from_datetime,
                to_datetime=self.to_datetime,
            )
        except crypto_provider_exceptions.ProviderError as e:
            msg = "Unable to import wallet transfers (currency={}, wallet_type={}). Error: {}".format(
                self.currency.name,
                self.wallet_type.name,
                common_utils.get_exception_message(exception=e),
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise CommandError(msg)
        except Exception as e:
            msg = "Unexpected exception occurred while importing wallet transfers. Error: {}".format(
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
            self.from_datetime = (
                datetime.datetime.fromisoformat(kwargs["from_datetime"])
                if kwargs["from_datetime"]
                else None
            )
            self.to_datetime = (
                datetime.datetime.fromisoformat(kwargs["to_datetime"])
                if kwargs["to_datetime"]
                else None
            )
            self.dry_run = kwargs["dry_run"]
        except Exception as e:
            msg = "Unable to setup config variables. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}. Exiting.".format(self.log_prefix, msg))
            raise CommandError(msg)
