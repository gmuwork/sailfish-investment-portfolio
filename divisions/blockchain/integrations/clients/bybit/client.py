import datetime
import decimal
import time
import typing
import urllib.parse

import requests
import hashlib
import hmac
import logging
import simplejson
from urllib import parse as url_parser

from django.conf import settings

from backend.divisions.blockchain.integrations.clients.bybit import enums
from backend.divisions.blockchain.integrations.clients.bybit import exceptions
from backend.divisions.common import enums as common_enums
from backend.divisions.common import utils as common_utils

logger = logging.getLogger(__name__)


class ByBitClient(object):
    API_BASE_URL = settings.BYBIT_API_URL
    API_KEY = settings.BYBIT_API_KEY
    API_SECRET_KEY = settings.BYBIT_API_SECRET_KEY
    VALID_STATUS_CODES = [200, 201, 204]
    REQUEST_EXPIRATION = 10000  # value in ms

    LOG_PREFIX = "[BYBIT-CLIENT]"

    def get_market_instruments(
        self,
        category: str,
        depth: int = 1,
        limit: int = 50,
        symbol: typing.Optional[str] = None,
    ) -> typing.List[dict]:
        params = {"limit": limit, "category": category}
        if symbol:
            params["symbol"] = symbol

        return self._get_paginated_response(
            endpoint="/derivatives/v3/public/instruments-info",
            method=common_enums.HttpMethod.GET,
            params=params,
            data_field="list",
            depth=depth,
        )

    def get_trade_orders(
        self,
        category: str,
        depth: int = 1,
        limit: int = 50,
        symbol: typing.Optional[str] = None,
        order_id: typing.Optional[str] = None,
        order_status: typing.Optional[str] = None,
        order_filter: typing.Optional[str] = None,
    ) -> typing.List[dict]:
        params = {"limit": limit, "category": category}

        if symbol:
            params["symbol"] = symbol

        if order_id:
            params["orderId"] = order_id

        if order_status:
            params["orderStatus"] = order_status

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
        self, symbol: str, category: str, limit: int = 50, depth: int = 1
    ) -> typing.List[dict]:
        return self._get_paginated_response(
            endpoint="/v5/position/list",
            method=common_enums.HttpMethod.GET,
            params={"symbol": symbol, "category": category, "limit": limit},
            data_field="list",
            depth=depth,
        )

    def get_trade_executions(
        self, symbol: str, category: str, order_id: str, limit: int = 50, depth: int = 1
    ) -> typing.List[dict]:
        return self._get_paginated_response(
            endpoint="/v5/execution/list",
            method=common_enums.HttpMethod.GET,
            params={
                "symbol": symbol,
                "category": category,
                "limit": limit,
                "orderId": order_id,
            },
            data_field="list",
            depth=depth,
        )

    def get_trade_positions_profit_and_loss(
        self,
        category: str,
        symbol: str,
        depth: int = 1,
        limit: int = 50,
        from_datetime: typing.Optional[datetime.datetime] = None,
        to_datetime: typing.Optional[datetime.datetime] = None,
    ) -> typing.List[dict]:
        params = {"symbol": symbol, "limit": limit, "category": category}

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

    def _get_response_content(self, response: requests.Response) -> dict:
        content = simplejson.loads(
            response.content,
            parse_float=decimal.Decimal,
        )

        # TODO: Later on map all codes and handle properly
        if content.get("retCode") != 0 or "result" not in content:
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
        headers = self._get_request_headers(
            signature_payload=self._construct_signature_payload(
                params=params, payload=payload, method=method
            )
        )

        try:
            response = requests.request(
                url=url,
                method=method.value,
                params=params,
                data=payload,
                headers=headers,
            )

            # ADD SECRET KEY OBFUSCATION
            if response.status_code not in self.VALID_STATUS_CODES:
                msg = "Invalid API client response (status_code={}, data={})".format(
                    response.status_code,
                    response.content.decode(encoding="utf-8"),
                )
                logger.error("{} {}.".format(self.LOG_PREFIX, msg))
                raise exceptions.BadResponseCodeErrpr(msg)
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

    def _construct_signature_payload(
        self,
        params: typing.Optional[dict],
        payload: typing.Optional[dict],
        method: common_enums.HttpMethod,
    ) -> str:
        payload = params if method == common_enums.HttpMethod.GET else payload
        if not payload:
            return ""

        if method == common_enums.HttpMethod.POST:
            return simplejson.dumps(payload)

        if method == common_enums.HttpMethod.GET:
            return urllib.parse.urlencode(payload)

        return ""

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
