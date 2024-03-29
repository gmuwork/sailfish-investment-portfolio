import datetime
import typing

from divisions.blockchain.integrations.clients.bybit import (
    client as rest_api_client,
)
from divisions.blockchain.integrations.clients.bybit import (
    enums as rest_api_client_enums,
)
from divisions.blockchain.integrations.clients.bybit import (
    exceptions as rest_api_client_exceptions,
)
from divisions.common import enums as common_enums
from divisions.common import utils as common_utils
from divisions.crypto import enums as crypto_enums
from divisions.crypto.integrations.provider import base
from divisions.crypto.integrations.provider import enums
from divisions.crypto.integrations.provider import exceptions
from divisions.crypto.integrations.provider import messages
from divisions.crypto.integrations.provider.bybit import schemas


class ByBitProvider(base.BaseProvider):
    def __init__(self):
        super(ByBitProvider, self).__init__()
        self._rest_api_client = None

    @property
    def provider(self) -> crypto_enums.CryptoProvider:
        return crypto_enums.CryptoProvider.BYBIT

    @property
    def rest_api_client_class(self) -> typing.Type[rest_api_client.ByBitClient]:
        return rest_api_client.ByBitClient

    def get_rest_api_client(self) -> rest_api_client.ByBitClient:
        if self._rest_api_client is None:
            self._rest_api_client = rest_api_client.ByBitClient()

        return self._rest_api_client

    def get_market_instruments(
        self,
        trading_category: enums.TradingCategory,
        depth: int = 1,
        limit: int = 50,
        market_instrument_symbol: typing.Optional[str] = None,
    ) -> typing.List[messages.MarketInstrument]:
        # TODO: Add trading category conversion to internal
        trading_category = trading_category
        try:
            response = self.get_rest_api_client().get_market_instruments(
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
                category=trading_category.convert_to_internal(provider=self.provider),
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = (
                "Unable to fetch market instruments from API"
                " (market_instrument_symbol={}, trading_category={}). Error: {}".format(
                    market_instrument_symbol,
                    trading_category.name,
                    common_utils.get_exception_message(exception=e),
                )
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.MarketInstruments()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Market instruments response data is not valid"
            )

        return [
            messages.MarketInstrument(
                name=market_instrument["symbol"], status=market_instrument["status"]
            )
            for market_instrument in validated_data["market_instruments"]
        ]

    def get_trade_positions(
        self,
        trading_category: enums.TradingCategory,
        currency: common_enums.Currency,
        depth: int = 1,
        limit: int = 50,
    ) -> typing.List[messages.TradePosition]:
        try:
            response = self.get_rest_api_client().get_trade_positions(
                depth=depth,
                currency=currency,
                category=trading_category.convert_to_internal(provider=self.provider),
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch trade positions from API (currency={}, category={}). Error: {}".format(
                currency.name,
                trading_category.name,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.TradePositions()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Trade positions response data is not valid"
            )

        return [
            messages.TradePosition(
                market_instrument_name=trade_position["symbol"],
                position_side=trade_position["side"],
                position_size=trade_position["size"],
                position_value=trade_position["value"],
                unrealised_pnl=trade_position["unrealised_pnl"],
                created_at=datetime.datetime.fromtimestamp(
                    trade_position["created_at"]
                ),
                updated_at=datetime.datetime.fromtimestamp(
                    trade_position["updated_at"]
                ),
            )
            for trade_position in validated_data["trade_positions"]
        ]

    def get_trade_positions_profit_and_loss(
        self,
        trading_category: enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[messages.TradePnLPosition]:
        if trading_category != enums.TradingCategory.LINEAR:
            msg = "Trading category {} not supported".format(trading_category.name)
            self.logger.error("{} {}.".format(self.log_prefix, msg))
            raise exceptions.TradingCategoryNotSupportedError(msg)

        try:
            response = self.get_rest_api_client().get_trade_positions_profit_and_loss(
                category=trading_category.convert_to_internal(provider=self.provider),
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch trade positions PnL from API (market_instrument_symbol={}, category={}, from_datetime={}, to_datetime={}). Error: {}".format(
                market_instrument_symbol,
                trading_category.name,
                from_datetime,
                to_datetime,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.TradePnLPositions()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Trade positions PnL response data is not valid"
            )

        return [
            messages.TradePnLPosition(
                market_instrument_name=trade_position["symbol"],
                position_side=trade_position["side"],
                order_id=trade_position["order_id"],
                position_quantity=trade_position["quantity"],
                order_price=trade_position["order_price"],
                order_type=trade_position["order_type"],
                position_closed_size=trade_position["closed_size"],
                total_entry_value=trade_position["total_entry_value"],
                average_entry_price=trade_position["average_entry_price"],
                total_exit_value=trade_position["total_exit_value"],
                average_exit_price=trade_position["average_exit_value"],
                closed_pnl=trade_position["closed_pnl"],
                created_at=datetime.datetime.fromtimestamp(
                    trade_position["created_at"]
                ),
            )
            for trade_position in validated_data["trade_pnl_positions"]
        ]

    def get_trade_orders(
        self,
        trading_category: enums.TradingCategory,
        depth: int = 1,
        limit: int = 50,
        market_instrument_symbol: typing.Optional[str] = None,
        order_id: typing.Optional[str] = None,
        order_status: typing.Optional[enums.TradeOrderStatus] = None,
        order_filter: typing.Optional[str] = None,
    ) -> typing.List[messages.TradeOrder]:
        try:
            response = self.get_rest_api_client().get_trade_orders(
                category=trading_category.convert_to_internal(provider=self.provider),
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
                order_id=order_id,
                order_status=order_status.convert_to_internal(provider=self.provider)
                if order_status
                else None,
                order_filter=order_filter,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch trade orders from API (market_instrument_symbol={}, category={}). Error: {}".format(
                market_instrument_symbol,
                trading_category.name,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.TradeOrders()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Trade orders response data is not valid"
            )

        return [
            messages.TradeOrder(
                market_instrument_name=trade_order["symbol"],
                order_id=trade_order["order_id"],
                order_side=trade_order["side"],
                order_quantity=trade_order["quantity"],
                order_price=trade_order["order_price"],
                average_order_price=trade_order["average_price"],
                order_type=trade_order["order_type"],
                order_status=trade_order["order_status"],
                order_total_executed_value=trade_order["total_executed_value"],
                order_total_executed_quantity=trade_order["total_executed_quantity"],
                order_total_executed_fee=trade_order["total_executed_fee"],
                created_at=datetime.datetime.fromtimestamp(trade_order["created_at"]),
                updated_at=datetime.datetime.fromtimestamp(trade_order["updated_at"]),
            )
            for trade_order in validated_data["trade_orders"]
        ]

    def get_trade_executions(
        self,
        trading_category: enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
        execution_type: typing.Optional[enums.TradeExecutionType] = None,
        order_id: typing.Optional[str] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[messages.TradeExecution]:
        try:
            response = self.get_rest_api_client().get_trade_executions(
                category=trading_category.convert_to_internal(provider=self.provider),
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
                order_id=order_id,
                execution_type=execution_type.convert_to_internal(
                    provider=self.provider
                )
                if execution_type
                else None,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch trade executions from API (market_instrument_symbol={}, category={}). Error: {}".format(
                market_instrument_symbol,
                trading_category.name,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.TradeExecutions()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Trade executions response data is not valid"
            )

        return [
            messages.TradeExecution(
                market_instrument_name=trade_execution["symbol"],
                order_id=trade_execution["order_id"],
                execution_id=trade_execution["execution_id"],
                execution_side=trade_execution["side"],
                executed_fee=trade_execution["executed_fee"],
                execution_price=trade_execution["execution_price"],
                execution_quantity=trade_execution["execution_quantity"],
                execution_type=trade_execution["execution_type"],
                execution_value=trade_execution["execution_value"],
                is_maker=trade_execution["is_maker"],
                created_at=datetime.datetime.fromtimestamp(
                    trade_execution["created_at"]
                ),
            )
            for trade_execution in validated_data["trade_executions"]
        ]

    def get_wallet_balances(
        self,
        wallet_type: enums.WalletType,
        currency: typing.Optional[common_enums.Currency] = None,
    ) -> typing.List[messages.WalletBalance]:
        try:
            response = self.get_rest_api_client().get_wallet_balances(
                account_type=wallet_type.convert_to_internal(provider=self.provider),
                currency=currency,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch wallet balances from API (wallet_type={}, currency={}). Error: {}".format(
                wallet_type.name,
                currency,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.WalletBalances()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Wallet balance response data is not valid"
            )

        return [
            messages.WalletBalance(
                currency=wallet_balance["currency"],
                amount=wallet_balance["amount"],
            )
            for wallet_balance in validated_data["wallet_balances"]
        ]

    def get_wallet_internal_transfers(
        self,
        wallet_type: enums.WalletType,
        depth: int = 1,
        limit: int = 50,
        currency: typing.Optional[common_enums.Currency] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[messages.WalletTransfer]:
        if wallet_type != enums.WalletType.DERIVATIVE:
            msg = (
                "Wallet type {} is not supported for internal wallet transfers".format(
                    wallet_type.name
                )
            )
            self.logger.info("{} {}. Exiting.".format(self.log_prefix, msg))
            raise exceptions.DataValidationError(msg)

        try:
            response = self.get_rest_api_client().get_wallet_internal_transfers(
                depth=depth,
                limit=limit,
                currency=currency,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch wallet internal transfers from API (currency={}). Error: {}".format(
                currency,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.WalletInternalTransfers()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Wallet internal transfers response data is not valid"
            )

        wallet_transfers = []
        for wallet_internal_transfer in validated_data["wallet_internal_transfers"]:
            from_recipient = enums.WalletType.convert_from_internal(
                wallet_type=rest_api_client_enums.AccountType(
                    wallet_internal_transfer["from_recipient"]
                )
            )
            to_recipient = enums.WalletType.convert_from_internal(
                wallet_type=rest_api_client_enums.AccountType(
                    wallet_internal_transfer["to_recipient"]
                )
            )

            if wallet_type not in [from_recipient, to_recipient]:
                self.logger.info(
                    "{} Wallet transfer (id={}) is not of type {}. Continue.".format(
                        self.log_prefix,
                        wallet_internal_transfer["transaction_id"],
                        wallet_type.name,
                    )
                )
                continue

            wallet_transfers.append(
                messages.WalletTransfer(
                    transaction_currency=wallet_internal_transfer["currency"],
                    chain_currency=common_utils.get_chain_currency(
                        currency=common_enums.Currency(
                            wallet_internal_transfer["currency"]
                        )
                    ).name,
                    type=enums.WalletTransferType.INTERNAL_DEPOSIT.value
                    if wallet_type == to_recipient
                    else enums.WalletTransferType.INTERNAL_WITHDRAWAL.value,
                    status=enums.WalletTransferStatus.convert_from_internal(
                        status=rest_api_client_enums.WalletInternalTransferStatus(
                            wallet_internal_transfer["status"]
                        )
                    ).value,
                    txid=wallet_internal_transfer["transaction_id"],
                    from_recipient=from_recipient.name,
                    to_recipient=to_recipient.name,
                    portfolio_type=wallet_type.name,
                    amount=wallet_internal_transfer["amount"],
                    fee=None,
                    network_datetime=datetime.datetime.fromtimestamp(
                        wallet_internal_transfer["created_at"]
                    ),
                )
            )

        return wallet_transfers
