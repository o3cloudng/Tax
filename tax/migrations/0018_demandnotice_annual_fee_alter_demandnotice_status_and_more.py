# Generated by Django 5.0.4 on 2024-09-03 13:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '0017_rename_paid_amount_demandnotice_amount_due_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandnotice',
            name='annual_fee',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='demandnotice',
            name='status',
            field=models.CharField(choices=[('DEMAND NOTICE', 'Demand Notice'), ('UNDISPUTED UNPAID', 'Undisputed Unpaid'), ('UNDISPUTED PAID', 'Undisputed Paid'), ('REVISED', 'Revised'), ('RESOLVED', 'Resolved')], default='UNPAID', max_length=30),
        ),
        migrations.AlterField(
            model_name='permit',
            name='year_installed',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 3, 14, 21, 0, 844595), max_length=200, null=True),
        ),
    ]
