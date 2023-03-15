import decimal

from django.db import models


# Create your models here.
class MarketInstrument(models.Model):
    name = models.CharField(max_length=255, null=False)
    status = models.CharField(max_length=255, null=False)
    provider = models.PositiveSmallIntegerField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_marketinstrument"
        unique_together = ["name", "provider"]


class TradeOrder(models.Model):
    # TODO: Instrument name can be FK to MarketInstrument
    instrument_name = models.CharField(max_length=255, null=False)
    order_id = models.CharField(max_length=255, null=False, unique=True)
    order_side = models.CharField(max_length=255, null=True)
    order_quantity = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    order_price = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    average_order_price = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    order_type = models.CharField(max_length=255, null=True)
    order_status = models.CharField(max_length=255, null=True)
    order_total_executed_value = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    order_total_executed_quantity = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    order_total_executed_fee = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    provider = models.PositiveSmallIntegerField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_tradeordertransaction"


class TradePnLTransaction(models.Model):
    position_closed_size = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    total_entry_value = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    average_entry_price = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    total_exit_value = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    average_exit_price = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    closed_pnl = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    created_at = models.DateTimeField()

    order = models.ForeignKey(
        TradeOrder, on_delete=models.CASCADE, related_name="pnl_transaction", null=True
    )

    class Meta:
        app_label = "crypto"
        db_table = "crypto_tradepnltransaction"


class TradeExecutionTransaction(models.Model):
    instrument_name = models.CharField(max_length=255, null=False)
    execution_id = models.CharField(max_length=255, null=False, unique=True)
    execution_side = models.CharField(max_length=255)
    execution_type = models.CharField(max_length=255)
    executed_fee = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    execution_price = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    execution_quantity = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    execution_value = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    is_maker = models.BooleanField(default=False)
    provider = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField()
    order = models.ForeignKey(
        TradeOrder, on_delete=models.CASCADE, related_name="execution_transaction", null=True
    )

    class Meta:
        app_label = "crypto"
        db_table = "crypto_tradeexecutiontransaction"
