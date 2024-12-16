# Generated by Django 5.1 on 2024-10-26 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("components", "0005_component_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="component",
            name="cost_price",
        ),
        migrations.RemoveField(
            model_name="component",
            name="selling_price",
        ),
        migrations.AddField(
            model_name="component",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=20, null=True
            ),
        ),
    ]
