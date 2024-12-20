# Generated by Django 5.1 on 2024-12-20 21:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assemblies", "0002_remove_assembly_package"),
        ("components", "0007_alter_component_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="component",
            name="assembly",
            field=models.ForeignKey(
                default="SMD",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="components",
                to="assemblies.assembly",
            ),
        ),
    ]