# Generated by Django 5.1 on 2024-12-20 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("assemblies", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="assembly",
            name="package",
        ),
    ]