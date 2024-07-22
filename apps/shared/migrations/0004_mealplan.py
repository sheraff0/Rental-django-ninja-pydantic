# Generated by Django 5.0 on 2023-12-15 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0003_alter_address_options_alter_amenity_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, verbose_name='TL code')),
                ('name', models.CharField(max_length=64, verbose_name='Title')),
            ],
            options={
                'verbose_name': 'Meal plan',
                'verbose_name_plural': 'Meal plans',
            },
        ),
    ]