# Generated by Django 4.2.10 on 2024-02-27 10:35

from django.db import migrations, models
import external.paykeeper.schemas


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0019_booking_corrupted'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='paykeeper_account',
            field=models.CharField(choices=[('mobile', 'MOBILE'), ('web', 'WEB')], default=external.paykeeper.schemas.PayKeeperAccount['MOBILE'], max_length=16, verbose_name='PayKeeper account'),
        ),
    ]
