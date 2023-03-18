import abc
import datetime
import logging
import typing

import marshmallow

from divisions.common import utils as common_utils
from divisions.crypto import enums as crypto_enums
from divisions.crypto.integrations.provider import enums
from divisions.crypto.integrations.provider import messages


class BaseProvider(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.log_prefix = "[{}-PROVIDER]".format(self.provider.name)

    @property
    @abc.abstractmethod
    def provider(self) -> crypto_enums.CryptoProvider:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def rest_api_client_class(self) -> typing.Callable:
        raise NotImplementedError

    @abc.abstractmethod
    def get_rest_api_client(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_market_instruments(
        self,
        trading_category: enums.TradingCategory,
        depth: int = 1,
        limit: int = 50,
        market_instrument_symbol: typing.Optional[str] = None,
    ) -> typing.List[messages.MarketInstrument]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_trade_positions(
        self,
        trading_category: enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
    ) -> typing.List[messages.TradePosition]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_trade_positions_profit_and_loss(
        self,
        trading_category: enums.TradingCategory,
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[messages.TradePnLPosition]:
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    def get_wallet_balances(
        self, wallet_type: enums.WalletType, currency: typing.Optional[str]
    ) -> typing.List[messages.WalletBalance]:
        pass

    def _validate_marshmallow_schema(
        self,
        data: typing.Union[dict, typing.List[dict]],
        schema: marshmallow.schema.Schema,
    ) -> typing.Optional[dict]:

        try:
            validated_data = schema.load(data=data, unknown=marshmallow.EXCLUDE)
        except marshmallow.exceptions.ValidationError as e:
            self.logger.error(
                "{} Provided data does not comply with validation schema. Errors: {}.".format(
                    self.log_prefix, common_utils.get_exception_message(exception=e)
                )
            )
            return None

        return validated_data
