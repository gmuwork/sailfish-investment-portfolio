"""
    1. Aggregation service should bring up performance by provider, trafing category, symbol, period
    2. Return message - Performance
    3. Create enum - time period
    4.
"""
import typing

from django.db import models as django_db_models

from backend.divisions.crypto import enums as crypto_enums
from backend.divisions.crypto.integrations.provider import enums as provider_enums
from backend.divisions.crypto.integrations.provider import messages as provider_messages
from backend.divisions.crypto.integrations.provider import factory
from divisions.crypto import models as crypto_models


def get_trade_position_performance(
    provider: crypto_enums.CryptoProvider,
    trading_category: provider_enums.TradingCategory,
    aggregation_period: crypto_enums.AggregationPeriod,
    symbol: typing.Optional[str] = None,
) -> typing.List[provider_messages.TradePositionPerformance]:
    aggregation_values = []
    aggregated_pnl_positions_qs = crypto_models.TradePnLTransaction.objects.filter(
        provider=provider.to_integer_choice(),
    )

    if symbol:
        aggregated_pnl_positions_qs = aggregated_pnl_positions_qs.filter(
            instrument_name=symbol
        )

    if aggregation_period == crypto_enums.AggregationPeriod.YEAR:
        aggregated_pnl_positions_qs = aggregated_pnl_positions_qs.annotate(
            year=django_db_models.functions.ExtractYear("created_at")
        )
        aggregation_values.extend(["year"])

    elif aggregation_period == crypto_enums.AggregationPeriod.MONTH:
        aggregated_pnl_positions_qs = aggregated_pnl_positions_qs.annotate(
            year=django_db_models.functions.ExtractYear("created_at"),
            month=django_db_models.functions.ExtractMonth("created_at"),
        )
        aggregation_values.extend(["year", "month"])

    elif aggregation_period == crypto_enums.AggregationPeriod.WEEK:
        aggregated_pnl_positions_qs = aggregated_pnl_positions_qs.annotate(
            year=django_db_models.functions.ExtractYear("created_at"),
            month=django_db_models.functions.ExtractMonth("created_at"),
            week=django_db_models.functions.ExtractWeek("created_at"),
        )
        aggregation_values.extend(["year", "month", "week"])

    elif aggregation_period == crypto_enums.AggregationPeriod.DAY:
        aggregated_pnl_positions_qs = aggregated_pnl_positions_qs.annotate(
            year=django_db_models.functions.ExtractYear("created_at"),
            month=django_db_models.functions.ExtractMonth("created_at"),
            week=django_db_models.functions.ExtractWeek("created_at"),
            day=django_db_models.functions.ExtractDay("created_at"),
        )
        aggregation_values.extend(["year", "month", "week", "day"])

    aggregated_pnl_positions = (
        aggregated_pnl_positions_qs.values(*aggregation_values)
        .annotate(pnl=django_db_models.Sum("closed_pnl"))
        .order_by("instrument_name")
        .values(*(aggregation_values + ["instrument_name", "pnl"]))
    )

    return [
        provider_messages.TradePositionPerformance(
            market_instrument_name=pnl_position["instrument_name"],
            pnl=pnl_position["pnl"],
            trading_category=trading_category,
            provider=provider,
            year=pnl_position.get("year"),
            month=pnl_position.get("month"),
            week=pnl_position.get("week"),
            day=pnl_position.get("day"),
        )
        for pnl_position in aggregated_pnl_positions
    ]
