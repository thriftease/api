# Generated by Django 5.0 on 2024-01-02 09:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('currencies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='currency',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='currencies.currency'),
        ),
    ]
