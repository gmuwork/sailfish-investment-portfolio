import datetime
import logging
import typing

from backend.divisions.common import utils as common_utils
from divisions.crypto import models as crypto_models
from backend.divisions.crypto.integrations.provider import base as base_provider_client
from backend.divisions.crypto.integrations.provider import enums as provider_enums
from backend.divisions.crypto.integrations.provider import (
    exceptions as provider_exceptions,
)
from backend.divisions.crypto.integrations.provider import messages as provider_messages


logger = logging.getLogger(__name__)


class CryptoProviderImporter(object):
    pass

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
                    " (market_instrument_symbol={}). Error: {}".format(
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

    def import_derivative_pnl_closed_transactions(
        self,
        market_instrument_symbol: str,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
        dry_run=False,
    ) -> None:
        """
        TODO: FINISH UP
        1. If not from_datetime and to_datetime
        2, Fetch latest pnl transaction and start fetching from that one
        3. If not transacions return
        4. Import each transaction
        """

        try:
            pnl_transactions = (
                self._provider_client.get_derivative_closed_positions_profit_and_loss(
                    market_instrument_symbol=market_instrument_symbol,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                    depth=1000,
                    limit=50,
                )
            )
        except provider_exceptions.ProviderError as e:
            msg = (
                "Unable to import pnl closed transactions ("
                " market_instrument_symbol={}). Error: {}".format(
                    market_instrument_symbol,
                    common_utils.get_exception_message(exception=e),
                )
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not pnl_transactions:
            logger.info(
                "{} No pnl closed transactions fetched (market_instrument_symbol={}). Exiting.".format(
                    self.log_prefix,
                    market_instrument_symbol,
                )
            )
            return None

        logger.info(
            "{} Fetched {} pnl closed transactions to import.".format(
                self.log_prefix, len(pnl_transactions)
            )
        )

        for pnl_transaction in pnl_transactions:
            try:
                self._import_pnl_transaction(
                    pnl_transaction=pnl_transaction, dry_run=dry_run
                )
            except Exception as e:
                msg = (
                    "Unexpected exception occurred while importing pnl transactions"
                    " (market_instrument_symbol={}). Error: {}".format(
                        pnl_transaction.market_instrument_name,
                        common_utils.get_exception_message(exception=e),
                    )
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))
                continue

    def _import_pnl_transaction(
        self, pnl_transaction: provider_messages.DerivativePnLPosition, dry_run: bool
    ) -> None:
        if crypto_models.DerivativePnLClosedTransaction.objects.filter(
            order_id=pnl_transaction.order_id,
            provider=self._provider_client.provider.to_integer_choice(),
        ).exists():
            logger.info(
                "{} PnL closed transaction already exists (market_instrument_symbol={}, order_id={}). Exiting.".format(
                    self.log_prefix,
                    pnl_transaction.market_instrument_name,
                    pnl_transaction.order_id,
                )
            )
            return None

        if dry_run:
            logger.info(
                "{} [DRY-RUN] Would create PnL closed transaction (market_instrument_symbol={}, order_id={}). Exiting.".format(
                    self.log_prefix,
                    pnl_transaction.market_instrument_name,
                    pnl_transaction.order_id,
                )
            )
        crypto_models.DerivativePnLClosedTransaction.objects.create(
            instrument_name=pnl_transaction.market_instrument_name,
            order_id=pnl_transaction.order_id,
            position_side=pnl_transaction.position_side,
            position_quantity=pnl_transaction.position_quantity,
            order_price=pnl_transaction.order_price,
            order_type=pnl_transaction.order_type,
            position_closed_size=pnl_transaction.position_closed_size,
            total_entry_value=pnl_transaction.total_entry_value,
            average_entry_price=pnl_transaction.average_entry_price,
            total_exit_value=pnl_transaction.total_exit_value,
            average_exit_price=pnl_transaction.average_exit_price,
            closed_pnl=pnl_transaction.closed_pnl,
            created_at=pnl_transaction.created_at,
            provider=self._provider_client.provider.to_integer_choice(),
        )

        logger.info(
            "{} Created PnL closed transaction (market_instrument_symbol={}, order_id={}).".format(
                self.log_prefix,
                pnl_transaction.market_instrument_name,
                pnl_transaction.order_id,
            )
        )
