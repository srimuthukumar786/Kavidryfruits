# Generated by Django 4.2.18 on 2025-01-29 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VegistApp', '0014_alter_product_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
