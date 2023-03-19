import datetime
import logging
import time
import typing

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from divisions.common import utils as common_utils
from divisions.crypto import enums as crypto_enums
from divisions.crypto.integrations.provider import factory as crypto_provider_factory
from divisions.crypto import models as crypto_models
from divisions.crypto.integrations.provider import enums as crypto_provider_enums
from divisions.crypto.integrations.provider.services import (
    data_importer as data_importer_services,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Imports trading data. More specifically it imports trade order, pnl and execution transactions.
            ex. python manage.py import_wallet_balances --provider=BYBIT --trading-category=LINEAR --number-of-pages=1 --from-datetime=2022-01-01 --to-datetime=2023-01-01 [--dry-run]
            """

    def add_arguments(self, parser):
        parser.add_argument(
            "--provider",
            help="Provider for which trading data is to be imported. One of CryptoProvider enum choices.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--trading-category",
            help="Trading category for which trading data is to be imported. One of TradingCategory enum choices.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--number-of-pages",
            help="Number of pages that are fetched from API to import data for each trading pair.",
            required=True,
            type=int,
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
    trading_category = None
    number_of_pages = None
    from_datetime = None
    to_datetime = None
    dry_run = None
    time_to_sleep = 1

    log_prefix = "[IMPORT-TRADING-DATA]"

    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._setup_config_variables(kwargs=kwargs)
        logger.info(
            "{} Started command '{}' (provider={}, trading_category={}, number_of_pages={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                self.provider.name,
                self.trading_category.name,
                self.number_of_pages,
            )
        )

        importer_service = data_importer_services.CryptoProviderImporter(
            provider_client=crypto_provider_factory.Factory(
                provider=self.provider
            ).create()
        )
        for market_instrument in (
            crypto_models.MarketInstrument.objects.filter(
                provider=self.provider.to_integer_choice(),
            )
            .values_list("name", flat=True)
            .iterator()
        ):
            logger.info(
                "{} Importing data (market_instrument_name={}).".format(
                    self.log_prefix, market_instrument
                )
            )
            try:
                importer_service.import_trade_orders(
                    trading_category=self.trading_category,
                    market_instrument_symbol=market_instrument,
                    depth=self.number_of_pages,
                    dry_run=self.dry_run,
                )

                importer_service.import_trade_pnl_transactions(
                    trading_category=self.trading_category,
                    market_instrument_symbol=market_instrument,
                    depth=self.number_of_pages,
                    from_datetime=self.from_datetime,
                    to_datetime=self.to_datetime,
                    dry_run=self.dry_run,
                )

                importer_service.import_trade_execution_transactions(
                    trading_category=self.trading_category,
                    market_instrument_symbol=market_instrument,
                    depth=self.number_of_pages,
                    from_datetime=self.from_datetime,
                    to_datetime=self.to_datetime,
                    dry_run=self.dry_run,
                )

                logger.info(
                    "{} Imported data (market_instrument_name={}). Sleeping {} seconds.".format(
                        self.log_prefix,
                        market_instrument,
                        self.time_to_sleep,
                    )
                )
                time.sleep(self.time_to_sleep)
            except Exception as e:
                msg = "Unexpected exception occurred while importing trading data. Error: {}".format(
                    common_utils.get_exception_message(exception=e)
                )
                logger.exception("{} {}. Continue,".format(self.log_prefix, msg))

        logger.info(
            "{} Finished command '{}' (provider={}, trading_category={}, number_of_pages={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                self.provider.name,
                self.trading_category.name,
                self.number_of_pages,
            )
        )

    def _setup_config_variables(self, kwargs: typing.Dict) -> None:
        try:
            self.provider = crypto_enums.CryptoProvider(kwargs["provider"])
            self.trading_category = crypto_provider_enums.TradingCategory(
                kwargs["trading_category"]
            )
            self.number_of_pages = kwargs["number_of_pages"]
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
