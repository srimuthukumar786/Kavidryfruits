# Generated by Django 4.2.18 on 2025-02-03 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VegistApp', '0025_alter_gallery_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='regular_price',
        ),
        migrations.AddField(
            model_name='product',
            name='price1',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True, verbose_name='Sale Price 100g'),
        ),
        migrations.AddField(
            model_name='product',
            name='price2',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True, verbose_name='Sale Price 250g'),
        ),
        migrations.AddField(
            model_name='product',
            name='price3',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True, verbose_name='Sale Price 500g'),
        ),
        migrations.AddField(
            model_name='product',
            name='price4',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True, verbose_name='Sale Price 1kg'),
        ),
    ]
