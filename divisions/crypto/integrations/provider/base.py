import abc
import datetime
import logging
import typing

import marshmallow

from backend.divisions.common import utils as common_utils
from backend.divisions.crypto import enums as crypto_enums
from backend.divisions.crypto.integrations.provider import enums
from backend.divisions.crypto.integrations.provider import messages


class BaseProvider(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
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
        depth: int = 1,
        limit: int = 50,
        trading_category: typing.Optional[enums.TradingCategory] = None,
        market_instrument_symbol: typing.Optional[str] = None,
    ) -> typing.List[messages.MarketInstrument]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_derivative_positions(
        self, market_instrument_symbol: str, depth: int = 1, limit: int = 50
    ) -> typing.List[messages.DerivativePosition]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_derivative_closed_positions_profit_and_loss(
        self,
        market_instrument_symbol: str,
        depth: int = 1,
        limit: int = 50,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[messages.DerivativePnLPosition]:
        raise NotImplementedError

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
