from django.db import models

# Create your models here.
class DerivativeTransaction(models.Model):
    symbol = models.CharField(max_length=255)

    class Meta(object):
        db_table = "blockchain_derivative_transaction"
        app_label = "blockchain"