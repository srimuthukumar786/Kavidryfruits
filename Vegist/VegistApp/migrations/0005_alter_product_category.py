# Generated by Django 4.2.18 on 2025-01-23 06:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('VegistApp', '0004_alter_category_image_alter_product_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='VegistApp.category'),
        ),
    ]
