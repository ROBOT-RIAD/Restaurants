import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from message.models import ChatMessage
from restaurant.models import Restaurant
from device.models import Device
from accounts.models import User
import logging
from .models import CallSession

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.user = self.scope['user']
        self.user_info = self.scope.get('user_info', {})

        self.restaurant_group_name = f"room_{self.device_id}_{self.user_info.get('restaurants_id')}"
        print("jjdjdjdjjdjdjjd",self.restaurant_group_name)

        if self.user and self.user.is_authenticated and (self.user.role in ["customer", "owner", "staff","chef"]):
            await self.channel_layer.group_add(self.restaurant_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.restaurant_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')
            if not message:
                raise ValueError("Missing message content")
        except Exception:
            await self.send(text_data=json.dumps({"error": "Invalid JSON or missing 'message' field"}))
            return

        # Determine sender and receiver
        if self.user.role == "customer":
            receiver = await self._get_restaurant_owner(self.user_info.get('restaurants_id'))
            is_from_device = True
        else:  # owner or staff
            receiver = await self._get_device_user(self.device_id)
            is_from_device = False

        sender = self.user

        chat_message = await self._save_message(
            sender=sender,
            receiver=receiver,
            message=message,
            device_id=self.device_id,
            restaurant_id=self.user_info.get('restaurants_id'),
            is_from_device=is_from_device,
            room_name=self.restaurant_group_name
        )

        if not chat_message:
            await self.send(text_data=json.dumps({"error": "Message could not be saved. Device or Restaurant may not exist."}))
            return

        # Broadcast the message
        await self.channel_layer.group_send(
            self.restaurant_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'is_from_device': is_from_device,
                'timestamp': str(chat_message.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'is_from_device': event['is_from_device'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def _save_message(self, sender, receiver, message, device_id, restaurant_id, is_from_device,room_name):
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            logger.warning(f"Device with ID {device_id} does not exist.")
            return None

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            logger.warning(f"Restaurant with ID {restaurant_id} does not exist.")
            return None

        return ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            device=device,
            restaurant=restaurant,
            is_from_device=is_from_device,
            room_name=room_name,
            new_message=True
        )

    @database_sync_to_async
    def _get_restaurant_owner(self, restaurant_id):
        return User.objects.filter(role='owner', restaurants__id=restaurant_id).first()


    @database_sync_to_async
    def _get_device_user(self, device_id):
        try:
            device = Device.objects.get(id=device_id)
            return device.user
        except Device.DoesNotExist:
            logger.warning(f"Device not found when fetching user. Device ID: {device_id}")
            return None
        

logger = logging.getLogger(__name__)
class CallSignalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.user = self.scope['user']
        self.group_name = f"call_{self.device_id}"

        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.debug(f"User {self.user} connected to {self.group_name}")
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        data = json.loads(text_data)
        action = data.get("action")
        message_type = data.get("type")

        if action == "start_call":
            await self.handle_start_call(data)
        elif action == "end_call":
            await self.handle_end_call(data)
        elif message_type in ["offer", "answer", "candidate"]:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'signal_message',
                    'message': json.dumps(data)
                }
            )

    async def signal_message(self, event):
        await self.send(text_data=event['message'])

    async def handle_start_call(self, data):
        receiver_id = data.get("receiver_id")
        device_id = data.get("device_id")
        offer = data.get("offer")

        if not (receiver_id and device_id and offer):
            await self.send(text_data=json.dumps({"error": "Missing receiver_id, device_id or offer"}))
            return

        await self.end_existing_calls(self.user.id)
        await self.create_call_session(self.user.id, receiver_id, device_id)

        await self.channel_layer.group_send(
            f"call_{device_id}",
            {
                'type': 'signal_message',
                'message': json.dumps({
                    "action": "incoming_call",
                    "from": self.user.username,
                    "device_id": device_id,
                    "type": "offer",
                    "offer": offer
                })
            }
        )

    async def handle_end_call(self, data):
        await self.end_existing_calls(self.user.id)
        device_id = data.get("device_id")
        if device_id:
            await self.channel_layer.group_send(
                f"call_{device_id}",
                {
                    'type': 'signal_message',
                    'message': json.dumps({
                        "action": "call_ended",
                        "by": self.user.username
                    })
                }
            )

    @database_sync_to_async
    def create_call_session(self, caller_id, receiver_id, device_id):
        try:
            caller = User.objects.get(id=caller_id)
            receiver = User.objects.get(id=receiver_id)
            device = Device.objects.get(id=device_id)
            return CallSession.objects.create(caller=caller, receiver=receiver, device=device)
        except Exception as e:
            logger.exception("Error creating call session")
            return None

    @database_sync_to_async
    def end_existing_calls(self, user_id):
        active_calls = CallSession.objects.filter(caller_id=user_id, is_active=True)
        for call in active_calls:
            call.end_call()
