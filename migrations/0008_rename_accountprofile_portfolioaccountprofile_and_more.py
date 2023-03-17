# Generated by Django 4.1.7 on 2023-03-17 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0007_alter_portfoliowalletbalancesnapshot_amount'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AccountProfile',
            new_name='PortfolioAccountProfile',
        ),
        migrations.RenameField(
            model_name='portfoliotransfer',
            old_name='investor',
            new_name='portfolio_user',
        ),
        migrations.AlterModelTable(
            name='portfolioaccountprofile',
            table='crypto_portfolioaccountprofile',
        ),
    ]
