# Generated by Django 5.0.4 on 2024-08-30 19:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '0011_infrastructure_processed_alter_permit_year_installed'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandnotice',
            name='is_exisiting',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='permit',
            name='year_installed',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 30, 20, 2, 12, 34029), max_length=200, null=True),
        ),
    ]
