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
        depth: int = 1,
        limit: int = 50,
        trading_category: typing.Optional[enums.TradingCategory] = None,
        market_instrument_symbol: typing.Optional[str] = None,
    ) -> typing.List[messages.MarketInstrument]:
        # TODO: Add trading category conversion to internal
        trading_category = trading_category
        try:
            response = self.get_rest_api_client().get_market_instruments(
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
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

    def get_derivative_positions(
        self, market_instrument_symbol: str, depth: int = 1, limit: int = 50
    ) -> typing.List[messages.DerivativePosition]:
        try:
            response = self.get_rest_api_client().get_derivative_positions(
                depth=depth,
                symbol=market_instrument_symbol,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch derivative positions from API (market_instrument_symbol={}). Error: {}".format(
                market_instrument_symbol,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.DerivativePositions()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Derivative positions response data is not valid"
            )

        return [
            messages.DerivativePosition(
                market_instrument_name=derivative_position["symbol"],
                position_side=derivative_position["side"],
                position_size=derivative_position["size"],
                position_value=derivative_position["value"],
                entry_price=derivative_position["entry_price"],
                created_at=datetime.datetime.fromtimestamp(
                    derivative_position["created_at"]
                ),
                updated_at=datetime.datetime.fromtimestamp(
                    derivative_position["updated_at"]
                ),
            )
            for derivative_position in validated_data["derivative_positions"]
        ]

    def get_derivative_closed_positions_profit_and_loss(
        self,
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[messages.DerivativePnLPosition]:
        try:
            response = self.get_rest_api_client().get_derivative_closed_positions_profit_and_loss(
                depth=depth,
                limit=limit,
                symbol=market_instrument_symbol,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            )
        except rest_api_client_exceptions.ByBitClientError as e:
            msg = "Unable to fetch derivative positions PnL from API (market_instrument_symbol={}, from_datetime={}, to_datetime={}). Error: {}".format(
                market_instrument_symbol,
                from_datetime,
                to_datetime,
                common_utils.get_exception_message(exception=e),
            )
            self.logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.APIClientError(msg)

        validated_data = self._validate_marshmallow_schema(
            data=response, schema=schemas.DerivativePnLPositions()
        )
        if not validated_data:
            raise exceptions.DataValidationError(
                "Derivative positions PnL response data is not valid"
            )

        return [
            messages.DerivativePnLPosition(
                market_instrument_name=derivative_position["symbol"],
                position_side=derivative_position["side"],
                order_id=derivative_position["order_id"],
                position_quantity=derivative_position["quantity"],
                order_price=derivative_position["order_price"],
                order_type=derivative_position["order_type"],
                position_closed_size=derivative_position["closed_size"],
                total_entry_value=derivative_position["total_entry_value"],
                average_entry_price=derivative_position["average_entry_price"],
                total_exit_value=derivative_position["total_exit_value"],
                average_exit_price=derivative_position["average_exit_value"],
                closed_pnl=derivative_position["closed_pnl"],
                created_at=datetime.datetime.fromtimestamp(
                    derivative_position["created_at"]
                ),
            )
            for derivative_position in validated_data["derivative_pnl_positions"]
        ]
