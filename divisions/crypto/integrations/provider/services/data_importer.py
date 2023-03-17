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


logger = logging.getLogger()


class CryptoProviderImporter(object):
    def __init__(self, provider_client: base_provider_client.BaseProvider) -> None:
        self._provider_client = provider_client
        self.log_prefix = "[{}-IMPORTER]".format(self._provider_client.provider.name)

    def import_market_instruments(
        self,
        trading_category: provider_enums.TradingCategory,
        depth: int = 1,
        market_instrument_symbol: typing.Optional[str] = None,
        dry_run=False,
    ) -> None:
        try:
            market_instruments = self._provider_client.get_market_instruments(
                depth=depth,
                limit=50,
                trading_category=trading_category,
                market_instrument_symbol=market_instrument_symbol,
            )
        except provider_exceptions.ProviderError as e:
            msg = "Unable to fetch market instruments (trading_category={}). Error: {}".format(
                trading_category.name,
                common_utils.get_exception_message(exception=e),
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not market_instruments:
            logger.info(
                "{} No market instruments to import (trading_category={}). Exiting.".format(
                    self.log_prefix,
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
                "{} Market instrument already exists (market_instrument_symbol={}). Continue.".format(
                    self.log_prefix, market_instrument.name
                )
            )
            return None

        if dry_run:
            logger.info(
                "{} [DRY-RUN] Would create market instrument (market_instrument_symbol={}). Continue.".format(
                    self.log_prefix, market_instrument.name
                )
            )
            return None

        crypto_models.MarketInstrument.objects.create(
            name=market_instrument.name,
            status=market_instrument.status,
            provider=self._provider_client.provider.to_integer_choice(),
        )
        logger.info(
            "{} Created market instrument (market_instrument_symbol={}).".format(
                self.log_prefix, market_instrument.name
            )
        )

    def import_trade_orders(
        self,
        trading_category: provider_enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
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
                depth=depth,
                limit=50,
            )
        except provider_exceptions.ProviderError as e:
            msg = (
                "Unable to import trade orders (trading_category={},"
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

        logger.info(
            "{} Fetched {} trade orders to import.".format(
                self.log_prefix, len(trade_orders)
            )
        )

        for trade_order in trade_orders:
            try:
                self._import_trade_order(trade_order=trade_order, dry_run=dry_run)
            except Exception as e:
                msg = "Unexpected exception occurred while importing trade order (market_instrument_symbol={}, order_id={}). Error: {}".format(
                    trade_order.market_instrument_name,
                    trade_order.order_id,
                    common_utils.get_exception_message(exception=e),
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))

    def _import_trade_order(
        self, trade_order: provider_messages.TradeOrder, dry_run: bool
    ) -> None:
        if crypto_models.TradeOrder.objects.filter(
            order_id=trade_order.order_id
        ).exists():
            logger.info(
                "{} Trade order already exists (market_instrument_symbol={},"
                " order_id={}). Exiting.".format(
                    self.log_prefix,
                    trade_order.market_instrument_name,
                    trade_order.order_id,
                )
            )
            return None

        if dry_run:
            logger.info(
                "{} [DRY-RUN] Would create trade order (market_instrument_symbol={}, order_id={}). Exiting.".format(
                    self.log_prefix,
                    trade_order.market_instrument_name,
                    trade_order.order_id,
                )
            )
            return None

        crypto_models.TradeOrder.objects.create(
            instrument_name=trade_order.market_instrument_name,
            order_id=trade_order.order_id,
            order_side=trade_order.order_side,
            order_quantity=trade_order.order_quantity,
            order_price=trade_order.order_price,
            average_order_price=trade_order.average_order_price,
            order_type=trade_order.order_type,
            order_status=trade_order.order_status,
            order_total_executed_value=trade_order.order_total_executed_value,
            order_total_executed_quantity=trade_order.order_total_executed_quantity,
            order_total_executed_fee=trade_order.order_total_executed_fee,
            created_at=trade_order.created_at,
            updated_at=trade_order.updated_at,
            provider=self._provider_client.provider.to_integer_choice(),
        )

        logger.info(
            "{} Created trade order (market_instrument_symbol={}, order_id={}). Exiting.".format(
                self.log_prefix,
                trade_order.market_instrument_name,
                trade_order.order_id,
            )
        )

    def import_trade_pnl_transactions(
        self,
        trading_category: provider_enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
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
                    order__isnull=False,
                    order__order_status=provider_enums.TradeOrderStatus.FILLED.value,
                    order__provider=self._provider_client.provider.to_integer_choice(),
                    order__instrument_name=market_instrument_symbol,
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
                    depth=depth,
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
            order__order_id=pnl_transaction.order_id,
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
            return None

        trade_order = crypto_models.TradeOrder.objects.filter(
            order_id=pnl_transaction.order_id,
            order_status__in=[
                provider_enums.TradeOrderStatus.FILLED.convert_to_internal(
                    provider=self._provider_client.provider
                ).value,
                provider_enums.TradeOrderStatus.CANCELLED.convert_to_internal(
                    provider=self._provider_client.provider
                ).value,
            ],
        ).first()

        # TODO: ADD SENDING OF MANAGER MAIL
        if not trade_order:
            logger.error(
                "{} No trade order found (market_instrument_symbol={}, order_id={}, order_statuses={}). Exiting.".format(
                    self.log_prefix,
                    pnl_transaction.market_instrument_name,
                    pnl_transaction.order_id,
                    [
                        provider_enums.TradeOrderStatus.FILLED.name,
                        provider_enums.TradeOrderStatus.CANCELLED.name,
                    ],
                )
            )
            return None

        crypto_models.TradePnLTransaction.objects.create(
            position_closed_size=pnl_transaction.position_closed_size,
            total_entry_value=pnl_transaction.total_entry_value,
            average_entry_price=pnl_transaction.average_entry_price,
            total_exit_value=pnl_transaction.total_exit_value,
            average_exit_price=pnl_transaction.average_exit_price,
            closed_pnl=pnl_transaction.closed_pnl,
            created_at=pnl_transaction.created_at,
            order=trade_order,
        )

        logger.info(
            "{} Created PnL transaction (market_instrument_symbol={}, order_id={}).".format(
                self.log_prefix,
                pnl_transaction.market_instrument_name,
                pnl_transaction.order_id,
            )
        )

    def import_trade_execution_transactions(
        self,
        trading_category: provider_enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
        execution_type: typing.Optional[provider_enums.TradeExecutionType] = None,
        order_id: typing.Optional[str] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
        dry_run=False,
    ) -> None:
        if bool(from_datetime) != bool(to_datetime):
            logger.info(
                "{} Provide either both from_datetime and to_datetime or neither. Exiting.".format(
                    self.log_prefix
                )
            )
            return None

        if not (from_datetime and to_datetime):
            last_execution_transaction_qs = (
                crypto_models.TradeExecutionTransaction.objects.filter(
                    instrument_name=market_instrument_symbol,
                    provider=self._provider_client.provider.to_integer_choice(),
                )
            )

            if execution_type:
                last_execution_transaction_qs = last_execution_transaction_qs.filter(
                    execution_type=execution_type.value
                )

            last_execution_transaction = last_execution_transaction_qs.order_by(
                "created_at"
            ).last()

            if not last_execution_transaction:
                logger.info(
                    "{} No execution transactions found in db (market_instrument_symbol={}, trading_category={}) Exiting.".format(
                        self.log_prefix,
                        market_instrument_symbol,
                        trading_category.name,
                    )
                )
                return None

            from_datetime = last_execution_transaction.created_at
        try:
            execution_transactions = self._provider_client.get_trade_executions(
                trading_category=trading_category,
                market_instrument_symbol=market_instrument_symbol,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
                execution_type=execution_type,
                order_id=order_id,
                depth=depth,
                limit=50,
            )
        except provider_exceptions.ProviderError as e:
            msg = (
                "Unable to import execution transactions ("
                " market_instrument_symbol={}, trading_category={}). Error: {}".format(
                    market_instrument_symbol,
                    trading_category.name,
                    common_utils.get_exception_message(exception=e),
                )
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not execution_transactions:
            logger.info(
                "{} No execution transactions fetched (market_instrument_symbol={}, trading_category={}). Exiting.".format(
                    self.log_prefix,
                    market_instrument_symbol,
                    trading_category.name,
                )
            )
            return None

        logger.info(
            "{} Fetched {} execution transactions to import.".format(
                self.log_prefix, len(execution_transactions)
            )
        )

        for execution_transaction in execution_transactions:
            try:
                self._import_execution_transaction(
                    execution_transaction=execution_transaction, dry_run=dry_run
                )
            except Exception as e:
                msg = "Unexpected exception occurred while importing execution transactions (market_instrument_symbol={}, execution_id={}). Error: {}".format(
                    execution_transaction.market_instrument_name,
                    execution_transaction.execution_id,
                    common_utils.get_exception_message(exception=e),
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))
                continue

    def _import_execution_transaction(
        self, execution_transaction: provider_messages.TradeExecution, dry_run: bool
    ) -> None:

        if crypto_models.TradeExecutionTransaction.objects.filter(
            execution_id=execution_transaction.execution_id,
        ).exists():
            logger.info(
                "{} Execution transaction already exists (market_instrument_symbol={}, execution_id={}). Exiting.".format(
                    self.log_prefix,
                    execution_transaction.market_instrument_name,
                    execution_transaction.execution_id,
                )
            )
            return None

        if dry_run:
            logger.info(
                "{} [DRY-RUN] Would create execution transaction (market_instrument_symbol={}, execution_id={}). Exiting.".format(
                    self.log_prefix,
                    execution_transaction.market_instrument_name,
                    execution_transaction.order_id,
                )
            )
            return None

        trade_order = crypto_models.TradeOrder.objects.filter(
            order_id=execution_transaction.order_id,
        ).first()

        crypto_models.TradeExecutionTransaction.objects.create(
            instrument_name=execution_transaction.market_instrument_name,
            execution_id=execution_transaction.execution_id,
            execution_side=execution_transaction.execution_side,
            execution_type=execution_transaction.execution_type,
            executed_fee=execution_transaction.executed_fee,
            execution_price=execution_transaction.executed_fee,
            execution_quantity=execution_transaction.execution_quantity,
            execution_value=execution_transaction.execution_value,
            is_maker=execution_transaction.is_maker,
            provider=self._provider_client.provider.to_integer_choice(),
            created_at=execution_transaction.created_at,
            order=trade_order,
        )

        logger.info(
            "{} Created execution transaction (market_instrument_symbol={}, execution_id={}).".format(
                self.log_prefix,
                execution_transaction.market_instrument_name,
                execution_transaction.order_id,
            )
        )

    def import_wallet_balances(
        self,
        wallet_type: provider_enums.WalletType,
        currency: typing.Optional[str] = None,
    ) -> None:
        try:
            wallet_balances = self._provider_client.get_wallet_balances(
                wallet_type=wallet_type,
                currency=currency,
            )
        except provider_exceptions.ProviderError as e:
            msg = "Unable to import wallet balances (wallet_type={}, currency={}). Error: {}".format(
                wallet_type.name,
                currency,
                common_utils.get_exception_message(exception=e),
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            # TODO: Send mail to managers
            return None

        if not wallet_balances:
            logger.info(
                "{} No wallet balances fetched (wallet_type={}, currency={}). Exiting.".format(
                    self.log_prefix,
                    wallet_type.name,
                    currency,
                )
            )
            return None

        logger.info(
            "{} Fetched wallet balances for {} currencies to import.".format(
                self.log_prefix, len(wallet_balances)
            )
        )

        for wallet_balance in wallet_balances:
            try:
                self._import_wallet_balance(
                    wallet_balance=wallet_balance,
                    wallet_type=wallet_type,
                )
            except Exception as e:
                msg = "Unexpected exception occurred while importing wallet balances (wallet_type={}, currency={}). Error: {}".format(
                    wallet_type.name,
                    currency,
                    common_utils.get_exception_message(exception=e),
                )
                logger.exception("{} {}. Continue.".format(self.log_prefix, msg))
                continue

    def _import_wallet_balance(
        self,
        wallet_balance: provider_messages.WalletBalance,
        wallet_type: provider_enums.WalletType,
    ) -> None:

        if crypto_models.PortfolioWalletBalanceSnapshot.objects.filter(
            provider=self._provider_client.provider.to_integer_choice(),
            type=wallet_type.name,
            currency=wallet_balance.currency_name,
        ).exists():
            logger.info(
                "{} Wallet balance snapshot exists (currency={}, wallet_type={}). Exiting.".format(
                    self.log_prefix, wallet_balance.currency_name, wallet_type.name
                )
            )
            return None

        crypto_models.PortfolioWalletBalanceSnapshot.objects.create(
            provider=self._provider_client.provider.to_integer_choice(),
            type=wallet_type.name,
            currency=wallet_balance.currency_name,
            amount=wallet_balance.amount,
            created_at=datetime.datetime.now(),
        )

        logger.info(
            "{} Created wallet balance snapshot (currency={}, wallet_type={}).".format(
                self.log_prefix, wallet_balance.currency_name, wallet_type.name
            )
        )
