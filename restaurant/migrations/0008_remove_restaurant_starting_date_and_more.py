# Generated by Django 5.2.1 on 2025-06-19 02:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_alter_restaurant_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='starting_date',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
