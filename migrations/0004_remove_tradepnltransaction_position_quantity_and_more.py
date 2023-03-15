# Generated by Django 4.1.7 on 2023-03-15 18:12

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0003_remove_tradepnltransaction_instrument_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tradepnltransaction',
            name='position_quantity',
        ),
        migrations.CreateModel(
            name='TradeExecutionTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument_name', models.CharField(max_length=255)),
                ('execution_id', models.CharField(max_length=255, unique=True)),
                ('execution_side', models.CharField(max_length=255)),
                ('execution_type', models.CharField(max_length=255)),
                ('executed_fee', models.DecimalField(decimal_places=8, default=Decimal('0'), max_digits=21)),
                ('execution_price', models.DecimalField(decimal_places=8, default=Decimal('0'), max_digits=21)),
                ('execution_quantity', models.DecimalField(decimal_places=8, default=Decimal('0'), max_digits=21)),
                ('execution_value', models.DecimalField(decimal_places=8, default=Decimal('0'), max_digits=21)),
                ('is_maker', models.BooleanField(default=False)),
                ('provider', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField()),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='execution_transaction', to='crypto.tradeorder')),
            ],
            options={
                'db_table': 'crypto_tradeexecutiontransaction',
            },
        ),
    ]
