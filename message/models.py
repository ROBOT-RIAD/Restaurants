from django.db import models
from accounts.models import User
from device.models import Device
from restaurant.models import Restaurant

# Create your models here.

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)

    message = models.TextField()
    is_from_device = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    room_name = models.CharField(max_length=255, blank=True, null=True)
    new_message = models.BooleanField(default=True)

    def __str__(self):
        if self.is_from_device:
            return f"Device Msg: {self.device} -> {self.restaurant}"
        else:
            return f"{self.sender} -> {self.receiver}"