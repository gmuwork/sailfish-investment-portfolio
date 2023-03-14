import datetime
import logging
import typing

from backend.divisions.blockchain.integrations.clients.bybit import (
    client as rest_api_client,
)
from backend.divisions.blockchain.integrations.clients.bybit import (
    exceptions as rest_api_client_exceptions,
)
from backend.divisions.common import utils as common_utils
from backend.divisions.crypto import enums as crypto_enums
from backend.divisions.crypto.integrations.provider import base
from backend.divisions.crypto.integrations.provider import enums
from backend.divisions.crypto.integrations.provider import exceptions
from backend.divisions.crypto.integrations.provider import messages
from backend.divisions.crypto.integrations.provider.bybit import schemas


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
                category=trading_category.value,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch market instruments from API (market_instrument_symbol={}, trading_category={}). Error: {}".format(
                market_instrument_symbol,
                trading_category.name,
                common_utils.get_exception_message(exception=e),
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
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
    ) -> typing.List[messages.TradePosition]:
        try:
            response = self.get_rest_api_client().get_trade_positions(
                depth=depth,
                symbol=market_instrument_symbol,
                category=trading_category.value,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch trade positions from API (market_instrument_symbol={}, category={}). Error: {}".format(
                market_instrument_symbol,
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
                entry_price=trade_position["entry_price"],
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
                category=trading_category.value,
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
                category=trading_category.value,
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
                order_id=order_id,
                order_status=order_status.value if order_status else None,
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
