# Generated by Django 5.0 on 2023-12-23 14:00

import apps.bookings.models.payment
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0007_alter_bookingdailyrate_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('waiting', 'WAITING'), ('failed', 'FAILED'), ('success', 'SUCCESS')], default='waiting', max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.FloatField(default=0, verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='refund',
            field=models.BooleanField(default=False, verbose_name='Refund'),
        ),
    ]
