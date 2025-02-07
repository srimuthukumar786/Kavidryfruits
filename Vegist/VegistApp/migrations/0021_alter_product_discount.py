# Generated by Django 4.2.18 on 2025-01-31 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VegistApp', '0020_product_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3, null=True),
        ),
    ]
