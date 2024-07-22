# Generated by Django 4.2.9 on 2024-02-14 14:32

import apps.bookings.models.payment
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0015_remove_payment_refund_payment_expiry'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='purpose',
            field=models.CharField(choices=[('prepayment', 'PREPAYMENT')], default=apps.bookings.models.payment.PaymentPurpose['PREPAYMENT'], max_length=32, verbose_name='Purpose'),
        ),
    ]
