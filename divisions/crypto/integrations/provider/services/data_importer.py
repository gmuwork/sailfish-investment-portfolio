import datetime
import logging
import typing

from backend.divisions.common import utils as common_utils
from backend.divisions.crypto.integrations.provider import base as base_provider_client
from backend.divisions.crypto.integrations.provider import enums as provider_enums
from backend.divisions.crypto.integrations.provider import (
    exceptions as provider_exceptions,
)
from backend.divisions.crypto.integrations.provider import messages as provider_messages
from divisions.crypto import models as crypto_models


logger = logging.getLogger(__name__)


class CryptoProviderImporter(object):
    def __init__(self, provider_client: base_provider_client.BaseProvider) -> None:
        self._provider_client = provider_client
        self.log_prefix = "[{}-IMPORTER]".format(self._provider_client.provider.name)

    def import_market_instruments(
        self,
        trading_category: provider_enums.TradingCategory,
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

    def import_trade_orders(
        self,
        trading_category: provider_enums.TradingCategory,
        market_instrument_symbol: str,
        order_status: typing.Optional[provider_enums.TradeOrderStatus] = None,
        order_id: typing.Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        try:
            trade_orders = self._provider_client.get_trade_orders(
                trading_category=trading_category,
                market_instrument_symbol=market_instrument_symbol,
                order_id=order_id,
                order_status=order_status,
            )
        except provider_exceptions.ProviderError as e:
            msg = (
                "Unable to import trade orders instruments (trading_category={},"
                " market_instrument_symbol={}). Error: {}".format(
                    trading_category.name,
                    market_instrument_symbol,
                    common_utils.get_exception_message(exception=e),
                )
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not trade_orders:
            logger.info(
                "{} No trade orders fetched (trading_category={}, market_instrument_symbol={}). Exiting.".format(
                    self.log_prefix, trading_category.name, market_instrument_symbol
                )
            )
            return None

        for trade_order in trade_orders:
            try:
                self._import_trade_order(trade_order=trade_order, dry_run=dry_run)
            except Exception as e:
                msg = "Unexpected exception occurred while importing trade order (market_instrument_symbol={}, trading_category={}). Error: {}".format(
                    trade_order.market_instrument_name,
                    trading_category.name,
                    common_utils.get_exception_message(exception=e),
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))

    def _import_trade_order(
        self, trade_order: crypto_models.TradeOrder, dry_run: bool
    ) -> None:
        pass

    def import_trade_pnl_transactions(
        self,
        trading_category: provider_enums.TradingCategory,
        market_instrument_symbol: str,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
        dry_run=False,
    ) -> None:
        if bool(from_datetime) != bool(to_datetime):
            logger.info(
                "{} Provider either both from_datetime and to_datetime or neither. Exiting.".format(
                    self.log_prefix
                )
            )
            return None

        if not (from_datetime and to_datetime):
            last_pnl_transaction = (
                crypto_models.TradePnLTransaction.objects.filter(
                    provider=self._provider_client.provider.to_integer_choice(),
                    instrument_name=market_instrument_symbol,
                )
                .order_by("created_at")
                .last()
            )

            if not last_pnl_transaction:
                logger.info(
                    "{} No PnL transactions found in db (market_instrument_symbol={}, trading_category={}) Exiting.".format(
                        self.log_prefix,
                        market_instrument_symbol,
                        trading_category.name,
                    )
                )
                return None

            from_datetime = last_pnl_transaction.created_at
        try:
            pnl_transactions = (
                self._provider_client.get_trade_positions_profit_and_loss(
                    trading_category=trading_category,
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
                " market_instrument_symbol={}, trading_category={}). Error: {}".format(
                    market_instrument_symbol,
                    trading_category.name,
                    common_utils.get_exception_message(exception=e),
                )
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not pnl_transactions:
            logger.info(
                "{} No PnL closed transactions fetched (market_instrument_symbol={}, trading_category={}). Exiting.".format(
                    self.log_prefix,
                    market_instrument_symbol,
                    trading_category.name,
                )
            )
            return None

        logger.info(
            "{} Fetched {} PnL transactions to import.".format(
                self.log_prefix, len(pnl_transactions)
            )
        )

        for pnl_transaction in pnl_transactions:
            try:
                self._import_pnl_transaction(
                    pnl_transaction=pnl_transaction, dry_run=dry_run
                )
            except Exception as e:
                msg = "Unexpected exception occurred while importing pnl transactions" " (market_instrument_symbol={}, trading_category={}). Error: {}".format(
                    pnl_transaction.market_instrument_name,
                    trading_category.name,
                    common_utils.get_exception_message(exception=e),
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))
                continue

    def _import_pnl_transaction(
        self, pnl_transaction: provider_messages.TradePnLPosition, dry_run: bool
    ) -> None:
        if crypto_models.TradePnLTransaction.objects.filter(
            order_id=pnl_transaction.order_id,
            provider=self._provider_client.provider.to_integer_choice(),
        ).exists():
            logger.info(
                "{} PnL transaction already exists (market_instrument_symbol={}, order_id={}). Exiting.".format(
                    self.log_prefix,
                    pnl_transaction.market_instrument_name,
                    pnl_transaction.order_id,
                )
            )
            return None

        if dry_run:
            logger.info(
                "{} [DRY-RUN] Would create PnL transaction (market_instrument_symbol={}, order_id={}). Exiting.".format(
                    self.log_prefix,
                    pnl_transaction.market_instrument_name,
                    pnl_transaction.order_id,
                )
            )
        crypto_models.TradePnLTransaction.objects.create(
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
            "{} Created PnL transaction (market_instrument_symbol={}, order_id={}).".format(
                self.log_prefix,
                pnl_transaction.market_instrument_name,
                pnl_transaction.order_id,
            )
        )
