# Generated by Django 5.0.3 on 2024-03-05 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0022_alter_booking_status_alter_bookinghistory_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='refunded',
            field=models.FloatField(default=0, verbose_name='Refunded amount'),
        ),
        migrations.DeleteModel(
            name='Refund',
        ),
    ]
