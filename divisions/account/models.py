from django.conf import settings
from django.db import models


class AccountProfile(models.Model):
    image_url = models.CharField(max_length=255, null=True, blank=True)
    referrer_uuid = models.CharField(max_length=255, null=False, unique=True)
    status = models.PositiveSmallIntegerField()  # TODO: Add enums

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_profile'
    )

    class Meta:
        app_label = "account"
        db_table = "account_profile"


class AccountTransaction(models.Model):
    address = models.CharField(max_length=255, null=True, blank=True)
    txid = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(
        decimal_places=8,
        max_digits=21,
    )
    net_amount = models.DecimalField(
        decimal_places=8,
        max_digits=21,
    )
    transfer_fee = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        null=True,
    )
    network_fee = models.DecimalField(
        decimal_places=8,
        max_digits=21,
        null=True,
    )
    type = models.PositiveSmallIntegerField()  # enum: AccountTransactionType
    status = models.PositiveSmallIntegerField()  # enum: AccountTransactionStatus
    currency = models.PositiveSmallIntegerField()  # enum: Currency
    datetime = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        app_label = "account"
        db_table = "account_transaction"


class AccountWalletBalance(models.Model):
    amount = models.DecimalField(
        decimal_places=8,
        max_digits=21,
    )
    type = models.PositiveSmallIntegerField()  # enum: AccountWalletBalanceType
    currency = models.PositiveSmallIntegerField()  # enum: Currency
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        app_label = "account"
        db_table = "account_walletbalance"