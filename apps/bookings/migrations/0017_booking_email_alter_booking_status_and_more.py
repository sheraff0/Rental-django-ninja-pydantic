# Generated by Django 4.2.10 on 2024-02-23 08:57

import apps.bookings.models.booking
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0016_payment_purpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('verified', 'VERIFIED'), ('confirmed', 'CONFIRMED'), ('rejected', 'REJECTED'), ('cancelled', 'CANCELLED')], default=apps.bookings.models.booking.BookingStatus['VERIFIED'], max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='bookinghistory',
            name='status',
            field=models.CharField(choices=[('verified', 'VERIFIED'), ('confirmed', 'CONFIRMED'), ('rejected', 'REJECTED'), ('cancelled', 'CANCELLED')], max_length=32),
        ),
    ]