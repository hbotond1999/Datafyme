# Generated by Django 5.1.4 on 2024-12-31 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporter_agent', '0004_alter_chart_meta_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='description',
            field=models.CharField(max_length=2500, null=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
