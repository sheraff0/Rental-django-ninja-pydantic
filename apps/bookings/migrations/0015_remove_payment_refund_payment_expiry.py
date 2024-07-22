# Generated by Django 4.2.9 on 2024-02-14 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0014_payment_invoice_url_payment_paykeeper_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='refund',
        ),
        migrations.AddField(
            model_name='payment',
            name='expiry',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Invoice expiry'),
        ),
    ]
