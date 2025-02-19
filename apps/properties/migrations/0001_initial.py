# Generated by Django 4.2.7 on 2023-12-03 17:49

import apps.properties.models.property
import apps.properties.models.room_type
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Last update time')),
                ('tl_id', models.IntegerField(blank=True, null=True, verbose_name='Id TravelLine')),
                ('name', models.CharField(max_length=128, verbose_name='Наименование')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.address', verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Объект размещения',
                'verbose_name_plural': 'Объекты размещения',
            },
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Last update time')),
                ('tl_id', models.IntegerField(blank=True, null=True, verbose_name='Id TravelLine')),
                ('name', models.CharField(max_length=128, verbose_name='Наименование')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.address', verbose_name='Адрес')),
                ('amenities', models.ManyToManyField(blank=True, to='shared.amenity')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.roomtypecategory')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_types', to='properties.property')),
            ],
            options={
                'verbose_name': 'Тип размещения',
                'verbose_name_plural': 'Типы размещения',
            },
        ),
        migrations.CreateModel(
            name='RoomTypeImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Last update time')),
                ('tl_id', models.CharField(blank=True, max_length=128, null=True, verbose_name='Id TravelLine')),
                ('image', models.ImageField(max_length=256, upload_to=apps.properties.models.room_type.RoomTypeImage.upload_to)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.roomtype')),
            ],
            options={
                'verbose_name': 'Картинка номера',
                'verbose_name_plural': 'Картинки номера',
            },
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create time')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Last update time')),
                ('tl_id', models.CharField(blank=True, max_length=128, null=True, verbose_name='Id TravelLine')),
                ('image', models.ImageField(max_length=128, upload_to=apps.properties.models.property.PropertyImage.upload_to)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.property')),
            ],
            options={
                'verbose_name': 'Картинка объекта',
                'verbose_name_plural': 'Картинки объекта',
            },
        ),
    ]
