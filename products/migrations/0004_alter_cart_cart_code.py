# Generated by Django 5.1.6 on 2025-02-17 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_cart_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_code',
            field=models.CharField(blank=True, max_length=11, null=True, unique=True),
        ),
    ]
