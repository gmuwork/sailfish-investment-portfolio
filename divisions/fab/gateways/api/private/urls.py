from django.urls import path

from divisions.fab.gateways.api.private.views import account
from divisions.fab.gateways.api.private.views import trading

urlpatterns = [
    path(
        "trade-orders",
        trading.TradeOrders.as_view(),
        name="trading.trade_orders",
    ),
    path(
        "register-user",
        account.AccountRegistration.as_view(),
        name="account.register_user",
    ),
]
