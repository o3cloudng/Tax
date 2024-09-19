# Generated by Django 5.0.4 on 2024-09-16 17:01

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '0025_alter_demandnotice_updated_at_delete_permit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalDemandNotice',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('referenceid', models.CharField(max_length=200, null=True)),
                ('is_exisiting', models.BooleanField(default=False)),
                ('infra', models.CharField(max_length=1000)),
                ('amount_due', models.PositiveIntegerField(default=0)),
                ('subtotal', models.PositiveIntegerField(default=0)),
                ('penalty', models.PositiveIntegerField(default=0)),
                ('application_fee', models.PositiveIntegerField(default=0)),
                ('admin_fee', models.PositiveIntegerField(default=0)),
                ('site_assessment', models.PositiveIntegerField(default=0)),
                ('annual_fee', models.PositiveIntegerField(default=0)),
                ('remittance', models.PositiveIntegerField(default=0)),
                ('waiver_applied', models.PositiveIntegerField(default=0)),
                ('amount_paid', models.PositiveIntegerField(default=0)),
                ('total_due', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('DEMAND NOTICE', 'Demand Notice'), ('UNDISPUTED UNPAID', 'Undisputed Unpaid'), ('UNDISPUTED PAID', 'Undisputed Paid'), ('REVISED', 'Revised'), ('RESOLVED', 'Resolved')], default='UNPAID', max_length=30)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('company', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical demand notice',
                'verbose_name_plural': 'historical demand notices',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalInfrastructure',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('length', models.IntegerField(default=0, null=True)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('year_installed', models.PositiveIntegerField(default=2024)),
                ('upload_application_letter', models.TextField(blank=True, max_length=100, null=True)),
                ('upload_asBuilt_drawing', models.TextField(blank=True, max_length=100, null=True)),
                ('is_existing', models.BooleanField(default=False)),
                ('processed', models.BooleanField(default=False)),
                ('referenceid', models.CharField(max_length=20, null=True)),
                ('cost', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('company', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('infra_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tax.infrastructuretype')),
            ],
            options={
                'verbose_name': 'historical infrastructure',
                'verbose_name_plural': 'historical infrastructures',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
