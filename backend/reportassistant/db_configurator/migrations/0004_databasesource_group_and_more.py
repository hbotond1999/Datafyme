# Generated by Django 5.1.3 on 2024-12-14 10:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('db_configurator', '0003_databasesource_is_paused'),
    ]

    operations = [
        migrations.AddField(
            model_name='databasesource',
            name='group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='databasesource',
            unique_together={('host', 'port', 'name')},
        ),
    ]
