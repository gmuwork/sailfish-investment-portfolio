import decimal
from django.db import models


class MarketInstrument(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    provider = models.PositiveSmallIntegerField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_marketinstrument"
        unique_together = ["name", "provider"]


class TradePosition(models.Model):
    instrument_name = models.CharField(max_length=255)
    unrealised_pnl = models.DecimalField(
        decimal_places=8,
        max_digits=21,
    )

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now_add=True)
    provider = models.PositiveSmallIntegerField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_tradeposition"
        unique_together = ["instrument_name", "unrealised_pnl", "provider"]


class TradeOrder(models.Model):
    # TODO: Instrument name can be FK to MarketInstrument
    instrument_name = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255, unique=True)
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
    instrument_name = models.CharField(max_length=255)
    execution_id = models.CharField(max_length=255, unique=True)
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
        TradeOrder,
        on_delete=models.CASCADE,
        related_name="execution_transaction",
        null=True,
    )

    class Meta:
        app_label = "crypto"
        db_table = "crypto_tradeexecutiontransaction"


class PortfolioAccountProfile(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_portfolioaccountprofile"


# LATER ON THIS CAN CONTAIN STATUS ETC - SOURCE TRUTH FOR CONNECTING INVESTOR WITH PORTFOLIO
class PortfolioAccountInvestmentParticipation(models.Model):
    portfolio_user = models.ForeignKey(
        PortfolioAccountProfile,
        on_delete=models.PROTECT,
        related_name="portfolio_investment_user",
    )
    investment_percentage = models.DecimalField(
        decimal_places=8,
        max_digits=21,
    )
    portfolio_id = models.SmallIntegerField(null=True, default=1)

    class Meta:
        app_label = "crypto"
        db_table = "crypto_portfolioaccountinvestmentparticipation"


class PortfolioTransfer(models.Model):
    provider = models.PositiveSmallIntegerField()
    transaction_currency = models.CharField(max_length=255)
    chain_currency = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    txid = models.CharField(max_length=255, null=True)
    from_recipient = models.CharField(max_length=255, null=True)
    to_recipient = models.CharField(max_length=255, null=True)
    portfolio_type = models.CharField(max_length=255)
    amount = models.DecimalField(
        decimal_places=8, max_digits=21, default=decimal.Decimal("0")
    )
    fee = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        null=True,
    )
    network_datetime = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    portfolio_user = models.ForeignKey(
        PortfolioAccountProfile,
        on_delete=models.PROTECT,
        related_name="account_transfer",
        null=True,
    )
    note = models.CharField(max_length=255, null=True)

    class Meta:
        app_label = "crypto"
        db_table = "crypto_portfoliotransfer"


class PortfolioWalletBalanceSnapshot(models.Model):
    provider = models.PositiveSmallIntegerField()
    portfolio_type = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    amount = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        default=decimal.Decimal("0"),
    )
    created_at = models.DateTimeField()

    class Meta:
        app_label = "crypto"
        db_table = "crypto_portfoliowalletbalance"
