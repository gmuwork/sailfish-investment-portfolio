import datetime
import decimal
import time
import typing

import requests
import hashlib
import hmac
import logging
import simplejson
from urllib import parse as url_parser

from django.conf import settings

from divisions.blockchain.integrations.clients.bybit import enums
from divisions.blockchain.integrations.clients.bybit import exceptions
from divisions.common import enums as common_enums
from divisions.common import utils as common_utils

logger = logging.getLogger(__name__)


class ByBitClient(object):
    API_BASE_URL = settings.BYBIT_API_URL
    API_KEY = settings.BYBIT_API_KEY
    API_SECRET_KEY = settings.BYBIT_API_SECRET_KEY
    VALID_STATUS_CODES = [200]
    REQUEST_EXPIRATION = 5000  # value in ms

    LOG_PREFIX = "[BYBIT-CLIENT]"

    def get_market_instruments(
        self,
        category: enums.TradingCategory,
        depth: int = 1,
        limit: int = 50,
        symbol: typing.Optional[str] = None,
    ) -> typing.List[dict]:
        params = {"limit": limit, "category": category.value}

        if symbol:
            params["symbol"] = symbol

        return self._get_paginated_response(
            endpoint="/v5/market/instruments-info",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def get_trade_orders(
        self,
        category: enums.TradingCategory,
        depth: int = 1,
        limit: int = 50,
        symbol: typing.Optional[str] = None,
        order_id: typing.Optional[str] = None,
        order_status: typing.Optional[enums.TradeOrderStatus] = None,
        order_filter: typing.Optional[str] = None,
    ) -> typing.List[dict]:
        params = {"limit": limit, "category": category.value}

        if symbol:
            params["symbol"] = symbol

        if order_id:
            params["orderId"] = order_id

        if order_status:
            params["orderStatus"] = order_status.value

        if order_filter:
            params["orderFilter"] = order_filter

        return self._get_paginated_response(
            endpoint="/v5/order/history",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def get_trade_positions(
        self,
        symbol: str,
        category: enums.TradingCategory,
        limit: int = 50,
        depth: int = 1,
    ) -> typing.List[dict]:
        return self._get_paginated_response(
            endpoint="/v5/position/list",
            method=common_enums.HttpMethod.GET,
            params={"symbol": symbol, "category": category.value, "limit": limit},
            data_field="list",
            depth=depth,
        )

    def get_trade_executions(
        self,
        category: enums.TradingCategory,
        symbol: str,
        limit: int = 50,
        depth: int = 1,
        execution_type: typing.Optional[enums.TradeExecutionType] = None,
        order_id: typing.Optional[str] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[dict]:
        params = {"limit": limit, "category": category.value, "symbol": symbol}

        if order_id:
            params["orderId"] = order_id

        if execution_type:
            params["execType"] = execution_type.value

        if from_datetime:
            params["startTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=from_datetime.timestamp()
            )

        if to_datetime:
            params["endTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=to_datetime.timestamp()
            )

        return self._get_paginated_response(
            endpoint="/v5/execution/list",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def get_trade_positions_profit_and_loss(
        self,
        category: enums.TradingCategory,
        symbol: str,
        depth: int = 1,
        limit: int = 50,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[dict]:
        params = {"symbol": symbol, "limit": limit, "category": category.value}

        if from_datetime:
            params["startTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=from_datetime.timestamp()
            )

        if to_datetime:
            params["endTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=to_datetime.timestamp()
            )

        return self._get_paginated_response(
            endpoint="/v5/position/closed-pnl",
            method=common_enums.HttpMethod.GET,
            params=params,
            depth=depth,
            data_field="list",
        )

    def get_transactions(
        self,
        depth: int = 1,
        limit: int = 50,
        account_type: typing.Optional[str] = None,
        category: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        transaction_type: typing.Optional[str] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[dict]:
        params = {"limit": limit}

        if account_type:
            params["accountType"] = account_type

        if category:
            params["category"] = category

        if currency:
            params["currency"] = currency

        if transaction_type:
            params["type"] = transaction_type

        if from_datetime:
            params["startTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=from_datetime.timestamp()
            )

        if to_datetime:
            params["endTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=to_datetime.timestamp()
            )

        return self._get_paginated_response(
            endpoint="/v5/account/transaction-log",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def get_wallet_balances(
        self,
        account_type: enums.AccountType,
        currency: typing.Optional[common_enums.Currency] = None,
    ) -> dict:
        params = {"accountType": account_type.value}

        if currency:
            params["coin"] = currency.value

        return self._get_response_content(
            response=self._request(
                endpoint="/asset/v3/private/transfer/account-coins/balance/query",
                method=common_enums.HttpMethod.GET,
                params=params,
            )
        )

    def get_wallet_internal_transfers(
        self,
        depth: int = 1,
        limit: int = 50,
        currency: typing.Optional[common_enums.Currency] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ):
        params = {
            "limit": limit,
        }
        if currency:
            params["coin"] = currency.value

        if from_datetime:
            params["startTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=from_datetime.timestamp()
            )

        if to_datetime:
            params["endTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=to_datetime.timestamp()
            )

        return self._get_paginated_response(
            endpoint="/v5/asset/transfer/query-inter-transfer-list",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def get_wallet_deposit_transfers(
        self,
        depth: int = 1,
        limit: int = 50,
        currency: typing.Optional[common_enums.Currency] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ):
        params = {
            "limit": limit,
        }
        if currency:
            params["coin"] = currency.value

        if from_datetime:
            params["startTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=from_datetime.timestamp()
            )

        if to_datetime:
            params["endTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=to_datetime.timestamp()
            )

        return self._get_paginated_response(
            endpoint="/v5/asset/deposit/query-record",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="rows",
            depth=depth,
        )

    def get_wallet_withdrawal_transfers(
        self,
        depth: int = 1,
        limit: int = 50,
        withdrawal_type: enums.WithdrawalType = enums.WithdrawalType.ALL,
        currency: typing.Optional[common_enums.Currency] = None,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ):
        params = {"limit": limit, "withdrawType": withdrawal_type.value}
        if currency:
            params["coin"] = currency.value

        if from_datetime:
            params["startTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=from_datetime.timestamp()
            )

        if to_datetime:
            params["endTime"] = common_utils.convert_timestamp_to_milliseconds(
                timestamp=to_datetime.timestamp()
            )

        return self._get_paginated_response(
            endpoint="/v5/asset/withdraw/query-record",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def _get_response_content(self, response: requests.Response) -> dict:
        content = simplejson.loads(
            response.content,
            parse_float=decimal.Decimal,
        )

        # TODO: Later on map all codes and handle properly
        if (
            content.get("retCode") != enums.StatusCode.OK.value
            or "result" not in content
        ):
            msg = "Invalid response content (response_data={})".format(
                response.content.decode(encoding="utf-8")
            )
            logger.error("{} {}.".format(self.LOG_PREFIX, msg))
            raise exceptions.ByBitClientError(msg)

        return content["result"]

    def _get_paginated_response(
        self,
        endpoint: str,
        method: common_enums.HttpMethod,
        depth: int,
        data_field: str,
        params: typing.Optional[dict] = None,
        payload: typing.Optional[dict] = None,
    ) -> typing.List[dict]:
        data = []

        for _ in range(depth):
            response = self._get_response_content(
                response=self._request(
                    endpoint=endpoint,
                    method=method,
                    params=params,
                    payload=payload,
                )
            )
            data.extend(response.get(data_field, []))

            if not response.get("nextPageCursor", False):
                break

            params["cursor"] = response["nextPageCursor"]

        return data

    def _request(
        self,
        endpoint: str,
        method: common_enums.HttpMethod,
        params: typing.Optional[dict] = None,
        payload: typing.Optional[dict] = None,
    ) -> requests.Response:
        url = url_parser.urljoin(base=self.API_BASE_URL, url=endpoint)
        signature_payload = self._construct_signature_payload(
            params=params, payload=payload, method=method
        )
        headers = self._get_request_headers(
            signature_payload=signature_payload if signature_payload else ""
        )

        try:
            response = requests.request(
                url=url,
                method=method.value,
                params=params,
                data=payload,
                headers=headers,
            )

            if response.status_code not in self.VALID_STATUS_CODES:
                msg = "Invalid API client response (status_code={}, data={})".format(
                    response.status_code,
                    response.content.decode(encoding="utf-8"),
                )
                logger.error("{} {}.".format(self.LOG_PREFIX, msg))
                raise exceptions.BadResponseCodeError(msg)
        except requests.exceptions.ConnectTimeout as e:
            msg = "Connect timeout. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}.".format(self.LOG_PREFIX, msg))
            raise exceptions.ByBitClientError(msg)
        except requests.RequestException as e:
            msg = "Request exception. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}.".format(self.LOG_PREFIX, msg))
            raise exceptions.ByBitClientError(msg)

        return response

    @staticmethod
    def _construct_signature_payload(
        params: typing.Optional[dict],
        payload: typing.Optional[dict],
        method: common_enums.HttpMethod,
    ) -> typing.Optional[str]:
        payload = params if method == common_enums.HttpMethod.GET else payload
        if not payload:
            return None

        if method == common_enums.HttpMethod.POST:
            return simplejson.dumps(payload)

        if method == common_enums.HttpMethod.GET:
            return url_parser.urlencode(payload)

        return None

    def _get_request_headers(self, signature_payload: str) -> dict:
        request_timestamp = str(
            int(common_utils.convert_timestamp_to_milliseconds(timestamp=time.time()))
        )
        request_signature = self._generate_request_signature(
            request_timestamp=request_timestamp, signature_payload=signature_payload
        )
        return {
            "X-BAPI-API-KEY": self.API_KEY,
            "X-BAPI-SIGN": request_signature,
            "X-BAPI-SIGN-TYPE": str(enums.SignatureType.HMAC.value),
            "X-BAPI-TIMESTAMP": request_timestamp,
            "X-BAPI-RECV-WINDOW": str(self.REQUEST_EXPIRATION),
            "Content-Type": "application/json",
        }

    def _generate_request_signature(
        self, request_timestamp: str, signature_payload: str
    ) -> str:
        param = (
            request_timestamp
            + self.API_KEY
            + str(self.REQUEST_EXPIRATION)
            + signature_payload
        )
        return hmac.new(
            key=bytes(self.API_SECRET_KEY, "utf-8"),
            msg=param.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
