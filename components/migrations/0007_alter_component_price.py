# Generated by Django 5.1 on 2024-10-30 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("components", "0006_remove_component_cost_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="component",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=20, null=True
            ),
        ),
    ]
