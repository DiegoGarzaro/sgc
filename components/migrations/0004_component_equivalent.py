# Generated by Django 5.1 on 2024-10-19 17:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0003_component_datasheet'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='equivalent',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('id__isnull', False)), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equivalents', to='components.component'),
        ),
    ]
