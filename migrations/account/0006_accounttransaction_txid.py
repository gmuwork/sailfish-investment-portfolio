# Generated by Django 4.1.7 on 2023-03-28 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_accounttransaction_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttransaction',
            name='txid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
