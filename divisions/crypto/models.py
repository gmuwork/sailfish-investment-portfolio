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


class TradePnLTransaction(models.Model):
    # TODO: Instrument name can be FK to MarketInstrument
    instrument_name = models.CharField(max_length=255, null=False)
    order_id = models.CharField(max_length=255, null=False, unique=True)
    position_side = models.CharField(max_length=255, null=False)
    position_quantity = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    order_price = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    order_type = models.CharField(max_length=255, null=False)
    position_closed_size = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    total_entry_value = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    average_entry_price = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    total_exit_value = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    average_exit_price = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    closed_pnl = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0"), null=False
    )
    created_at = models.DateTimeField()
    provider = models.PositiveSmallIntegerField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_tradepnltransaction"
