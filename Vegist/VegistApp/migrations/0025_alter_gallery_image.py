# Generated by Django 4.2.18 on 2025-02-03 05:27

import VegistApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VegistApp', '0024_alter_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='image',
            field=models.ImageField(upload_to=VegistApp.models.getFilename),
        ),
    ]
