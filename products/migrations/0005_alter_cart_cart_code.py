# Generated by Django 5.1.6 on 2025-02-17 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_cart_cart_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_code',
            field=models.CharField(max_length=11, unique=True),
        ),
    ]
