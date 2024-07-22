# Generated by Django 5.0 on 2023-12-22 15:02

import apps.bookings.models.booking
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_alter_booking_number_alter_bookingdailyrate_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('verified', 'VERIFIED'), ('created', 'CREATED'), ('cancelled', 'CANCELLED')], default=apps.bookings.models.booking.BookingStatus['VERIFIED'], max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='bookinghistory',
            name='status',
            field=models.CharField(choices=[('verified', 'VERIFIED'), ('created', 'CREATED'), ('cancelled', 'CANCELLED')], max_length=32),
        ),
    ]