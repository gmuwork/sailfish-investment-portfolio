from django.db import models


# Create your models here.
class MarketInstrument(models.Model):
    name = models.CharField(max_length=255, null=False)
    status = models.CharField(max_length=255, null=False)
    provider = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "crypto_marketinstrument"
        unique_together = ["name", "provider"]

    # def get_provider(self) -> crypto_enums.CryptoProvider:
    #     return crypto_enums.CryptoProvider.from_integer_choice(choice=self.provider)
