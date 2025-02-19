# Generated by Django 4.2.7 on 2023-12-07 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0003_alter_address_options_alter_amenity_options_and_more'),
        ('properties', '0003_alter_roomtype_options_roomtype_sort_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'verbose_name': 'Property object', 'verbose_name_plural': 'Property objects'},
        ),
        migrations.AlterModelOptions(
            name='propertyimage',
            options={'ordering': ['sort_order'], 'verbose_name': 'Property image', 'verbose_name_plural': 'Property images'},
        ),
        migrations.AlterModelOptions(
            name='roomtype',
            options={'ordering': ['sort_order'], 'verbose_name': 'Room type', 'verbose_name_plural': 'Room types'},
        ),
        migrations.AlterModelOptions(
            name='roomtypeimage',
            options={'ordering': ['sort_order'], 'verbose_name': 'Room type image', 'verbose_name_plural': 'Room type images'},
        ),
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.address', verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='property',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='property',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='property',
            name='tl_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='TL id'),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='tl_id',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='TL id'),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.address', verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='tl_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='TL id'),
        ),
        migrations.AlterField(
            model_name='roomtypeimage',
            name='tl_id',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='TL id'),
        ),
    ]
