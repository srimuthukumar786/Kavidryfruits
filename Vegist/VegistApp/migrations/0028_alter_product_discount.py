# Generated by Django 4.2.18 on 2025-02-04 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VegistApp', '0027_alter_review_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
