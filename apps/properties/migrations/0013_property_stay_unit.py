# Generated by Django 5.0 on 2023-12-27 07:27

import apps.properties.models.property
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0012_roomtype_bedrooms_roomtype_elevator_roomtype_rooms_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='stay_unit',
            field=models.CharField(choices=[('NightRate', 'NIGHT_RATE'), ('DailyRate', 'DAILY_RATE')], default=apps.properties.models.property.StayUnit['NIGHT_RATE'], max_length=32),
        ),
    ]
