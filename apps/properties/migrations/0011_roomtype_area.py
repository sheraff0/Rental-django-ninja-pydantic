# Generated by Django 5.0 on 2023-12-23 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0010_roomtype_beds'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomtype',
            name='area',
            field=models.FloatField(blank=True, null=True, verbose_name='Area'),
        ),
    ]
