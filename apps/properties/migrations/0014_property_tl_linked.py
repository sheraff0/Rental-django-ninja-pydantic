# Generated by Django 4.2.9 on 2024-01-11 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0013_property_stay_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='tl_linked',
            field=models.BooleanField(default=False, verbose_name='Linked to TravelLine'),
        ),
    ]
