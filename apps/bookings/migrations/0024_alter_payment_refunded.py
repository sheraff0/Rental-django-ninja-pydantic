# Generated by Django 5.0.3 on 2024-03-05 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0023_payment_refunded_delete_refund'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='refunded',
            field=models.FloatField(blank=True, null=True, verbose_name='Refunded amount'),
        ),
    ]
