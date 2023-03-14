import typing

from marshmallow import fields
from marshmallow import pre_load
from marshmallow import post_load
from marshmallow import EXCLUDE
from marshmallow import schema

# TODO: Create common_schema
class MarketInstrument(schema.Schema):
    class Meta:
        unknown = EXCLUDE

    symbol = fields.Str(required=True, data_key="symbol")
    status = fields.Str(required=True, data_key="status")


class MarketInstruments(schema.Schema):
    market_instruments = fields.Nested(MarketInstrument, many=True)

    @pre_load
    def prepare_data(self, data: typing.List[dict], **kwargs: typing.Any) -> dict:
        return {"market_instruments": data}


class TradePosition(schema.Schema):
    class Meta:
        unknown = EXCLUDE

    symbol = fields.Str(required=True, data_key="symbol")
    side = fields.Str(required=True, allow_none=True, data_key="side")
    size = fields.Decimal(required=True, data_key="size")
    value = fields.Decimal(required=True, data_key="positionValue")
    entry_price = fields.Decimal(required=True, data_key="entryPrice")
    created_at = fields.Integer(required=True, data_key="createdTime")
    updated_at = fields.Integer(required=True, data_key="updatedTime")

    @post_load
    def prepare_data(self, data: dict, **kwargs: typing.Any) -> dict:
        data["created_at"] = data["created_at"] // 1000
        data["updated_at"] = data["updated_at"] // 1000
        return data


class TradePositions(schema.Schema):
    trade_positions = fields.Nested(TradePosition, many=True)

    @pre_load
    def prepare_data(self, data: typing.List[dict], **kwargs: typing.Any) -> dict:
        return {"trade_positions": data}


class TradePnLPosition(schema.Schema):
    class Meta:
        unknown = EXCLUDE

    symbol = fields.Str(required=True, data_key="symbol")
    order_id = fields.Str(required=True, data_key="orderId")
    side = fields.Str(required=True, allow_none=True, data_key="side")
    quantity = fields.Decimal(required=True, data_key="qty")
    order_price = fields.Decimal(required=True, data_key="orderPrice")
    order_type = fields.Str(required=True, data_key="orderType")
    closed_size = fields.Decimal(required=True, data_key="closedSize")
    total_entry_value = fields.Decimal(required=True, data_key="cumEntryValue")
    average_entry_price = fields.Decimal(required=True, data_key="avgEntryPrice")
    total_exit_value = fields.Decimal(required=True, data_key="cumExitValue")
    average_exit_value = fields.Decimal(required=True, data_key="avgExitPrice")
    closed_pnl = fields.Decimal(required=True, data_key="closedPnl")
    created_at = fields.Integer(required=True, data_key="createdAt")

    @post_load
    def prepare_data(self, data: dict, **kwargs: typing.Any) -> dict:
        data["created_at"] = data["created_at"] // 1000
        return data


class TradePnLPositions(schema.Schema):
    trade_pnl_positions = fields.Nested(TradePnLPosition, many=True)

    @pre_load
    def prepare_data(self, data: typing.List[dict], **kwargs: typing.Any) -> dict:
        return {"trade_pnl_positions": data}


class TradeOrder(schema.Schema):
    class Meta:
        unknown = EXCLUDE

    symbol = fields.Str(required=True, data_key="symbol")
    order_id = fields.Str(required=True, data_key="orderId")
    side = fields.Str(required=True, allow_none=True, data_key="side")
    quantity = fields.Decimal(required=True, data_key="qty")
    order_price = fields.Decimal(required=True, data_key="price")
    average_price = fields.Decimal(required=True, data_key="avgPrice")
    order_type = fields.Str(required=True, data_key="orderType")
    order_status = fields.Str(required=True, data_key="orderStatus")
    total_executed_value = fields.Decimal(required=True, data_key="cumExecValue")
    total_executed_quantity = fields.Decimal(required=True, data_key="cumExecQty")
    total_executed_fee = fields.Decimal(required=True, data_key="cumExecFee")
    created_at = fields.Integer(required=True, data_key="createdTime")
    updated_at = fields.Integer(required=True, data_key="updatedTime")

    @post_load
    def prepare_data(self, data: dict, **kwargs: typing.Any) -> dict:
        data["created_at"] = data["created_at"] // 1000
        data["updated_at"] = data["updated_at"] // 1000

        return data


class TradeOrders(schema.Schema):
    trade_orders = fields.Nested(TradeOrder, many=True)

    @pre_load
    def prepare_data(self, data: typing.List[dict], **kwargs: typing.Any) -> dict:
        return {"trade_orders": data}
