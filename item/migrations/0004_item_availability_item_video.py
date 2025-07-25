# Generated by Django 5.2.1 on 2025-05-24 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0003_alter_item_image1_alter_item_image2'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='availability',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='item',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='medea/item_videos/'),
        ),
    ]
