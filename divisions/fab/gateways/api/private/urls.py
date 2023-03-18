from django.urls import path

from divisions.fab.gateways.api.private import trading

urlpatterns = [
    path(
        "private-api/trade-orders",
        trading.TradeOrders.as_view(),
        name="trading.trade_orders",
    ),
]
