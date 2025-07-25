# Generated by Django 5.2.1 on 2025-05-22 08:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_otp'),
        ('restaurant', '0002_alter_restaurant_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChefStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('hold', 'Hold')], default='pending', max_length=10)),
                ('generate', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chefstaffs', to='restaurant.restaurant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
