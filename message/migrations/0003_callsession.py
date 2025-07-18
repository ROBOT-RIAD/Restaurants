# Generated by Django 5.2.1 on 2025-06-29 08:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0007_alter_reservation_email_alter_reservation_status'),
        ('message', '0002_chatmessage_new_message_chatmessage_room_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CallSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_calls', to=settings.AUTH_USER_MODEL)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='device.device')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_calls', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
