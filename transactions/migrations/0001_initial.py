# Generated by Django 5.0 on 2024-01-02 13:38

import django.db.models.deletion
import transactions.models
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_alter_account_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=18)),
                ('datetime', models.DateTimeField(blank=True, default=transactions.models.Transaction.auto_now_add)),
                ('name', models.CharField(blank=True, default='', max_length=50)),
                ('description', models.TextField(blank=True, default='', max_length=250)),
                ('account', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounts.account')),
            ],
        ),
    ]
