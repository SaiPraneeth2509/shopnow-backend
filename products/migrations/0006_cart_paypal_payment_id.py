# Generated by Django 5.1.6 on 2025-02-17 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_cart_cart_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='paypal_payment_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
