# Generated by Django 5.2.1 on 2025-05-25 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='table_name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
