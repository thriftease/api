# Generated by Django 5.0 on 2023-12-18 15:34

import utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=128, validators=[utils.validate_password])),
                ('given_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, default='', max_length=50)),
                ('family_name', models.CharField(max_length=50)),
                ('suffix', models.CharField(blank=True, default='', max_length=20)),
                ('is_admin', models.BooleanField(blank=True, default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
