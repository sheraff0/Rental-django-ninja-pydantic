# Generated by Django 4.2.7 on 2023-12-18 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0004_mealplan'),
        ('bookings', '0002_alter_search_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.city'),
        ),
    ]
