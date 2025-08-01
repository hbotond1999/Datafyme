# Generated by Django 5.1.5 on 2025-01-26 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporter_agent', '0005_alter_chart_description_alter_chart_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='type',
            field=models.CharField(choices=[('BAR', 'BAR_CHART'), ('LINE', 'LINE_CHART'), ('BUBBLE', 'BUBBLE_CHART'), ('HISTOGRAM', 'HISTOGRAM'), ('SCATTER', 'SCATTER_CHART'), ('PIE', 'PIE_CHART'), ('MIXED_CHART', 'MIXED_CHART'), ('STACK_BAR_CHART', 'STACK_BAR_CHART'), ('TABLE', 'TABLE')], max_length=100),
        ),
    ]
