# Generated by Django 5.0.4 on 2024-09-16 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tax', '0024_alter_demandnotice_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demandnotice',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='Permit',
        ),
    ]
