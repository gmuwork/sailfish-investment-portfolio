import logging
import typing

from backend.divisions.common import utils as common_utils
from backend.divisions.crypto import models as crypto_models
from backend.divisions.crypto.integrations.provider import base as base_provider_client
from backend.divisions.crypto.integrations.provider import enums as provider_enums
from backend.divisions.crypto.integrations.provider import (
    exceptions as provider_exceptions,
)
from backend.divisions.crypto.integrations.provider import messages as provider_messages


logger = logging.getLogger(__name__)


class CryptoProviderImporter(object):
    def __init__(self, provider_client: base_provider_client.BaseProvider) -> None:
        self._provider_client = provider_client
        self.log_prefix = "[{}-IMPORTER]".format(self._provider_client.provider.name)

    def import_market_instruments(
        self,
        trading_category: typing.Optional[provider_enums.TradingCategory] = None,
        market_instrument_symbol: typing.Optional[str] = None,
        dry_run=False,
    ) -> None:
        try:
            market_instruments = self._provider_client.get_market_instruments(
                depth=100,
                limit=500,
                trading_category=trading_category,
                market_instrument_symbol=market_instrument_symbol,
            )
        except provider_exceptions.ProviderError as e:
            msg = (
                "Unable to import market instruments (trading_category={},"
                " market_instrument_symbol={}). Error: {}".format(
                    trading_category.name if trading_category else None,
                    market_instrument_symbol,
                    common_utils.get_exception_message(exception=e),
                )
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not market_instruments:
            logger.info(
                "{} No market instruments fetched (trading_category={},"
                " market_instrument_symbol={}). Exiting.".format(
                    self.log_prefix,
                    trading_category.name if trading_category else None,
                    market_instrument_symbol,
                )
            )
            return None

        logger.info(
            "{} Fetched {} market instruments to import".format(
                self.log_prefix, len(market_instruments)
            )
        )

        for market_instrument in market_instruments:
            try:
                self._import_market_instrument(
                    market_instrument=market_instrument, dry_run=dry_run
                )
            except Exception as e:
                msg = (
                    "Unexpected exception occurred while importing market instrument"
                    " (name={}). Error: {}".format(
                        market_instrument.name,
                        common_utils.get_exception_message(exception=e),
                    )
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))
                continue

    def _import_market_instrument(
        self, market_instrument: provider_messages.MarketInstrument, dry_run: bool
    ) -> None:
        if crypto_models.MarketInstrument.objects.filter(
            name=market_instrument.name,
            provider=self._provider_client.provider.to_integer_choice(),
        ).exists():
            logger.info(
                "{} Market instrument already exists (name={}). Exiting.".format(
                    self.log_prefix, market_instrument.name
                )
            )
            return None

        if dry_run:
            logger.info(
                "{} [DRY-RUN] Would create market instrument (name={}). Exiting.".format(
                    self.log_prefix, market_instrument.name
                )
            )
        crypto_models.MarketInstrument.objects.create(
            name=market_instrument.name,
            status=market_instrument.status,
            provider=self._provider_client.provider.to_integer_choice(),
        )

        logger.info(
            "{} Created market instrument (name={}).".format(
                self.log_prefix, market_instrument.name
            )
        )
