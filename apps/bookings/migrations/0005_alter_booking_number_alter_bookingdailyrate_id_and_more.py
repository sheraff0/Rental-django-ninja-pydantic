# Generated by Django 4.2.7 on 2023-12-22 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_booking_payment_bookinghistory_bookingdailyrate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='number',
            field=models.CharField(max_length=64, null=True, verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='bookingdailyrate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='bookinghistory',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
