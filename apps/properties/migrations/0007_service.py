# Generated by Django 5.0 on 2023-12-15 08:18

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_alter_rateplan_options_remove_rateplan_sort_order'),
        ('shared', '0004_mealplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Last update time')),
                ('tl_id', models.IntegerField(blank=True, null=True, verbose_name='TL id')),
                ('name', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('meal_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='shared.mealplan')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='properties.property')),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
                'ordering': ['sort_order'],
            },
        ),
    ]