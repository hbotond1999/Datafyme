# Generated by Django 5.1.3 on 2024-12-14 16:39

import db_configurator.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_configurator', '0007_databasesource_is_ready'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='databasesource',
            name='is_paused',
        ),
        migrations.RemoveField(
            model_name='databasesource',
            name='is_ready',
        ),
        migrations.AddField(
            model_name='databasesource',
            name='status',
            field=models.CharField(choices=[('PAUSED', 'PAUSED'), ('LOADING', 'LOADING'), ('READY', 'READY'), ('ERROR', 'ERROR')], default=db_configurator.models.Status['LOADING'], max_length=50),
        ),
    ]
