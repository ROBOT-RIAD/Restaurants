from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<device_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/call/(?P<device_id>\w+)/$', consumers.CallSignalConsumer.as_asgi()),
    re_path(r'ws/order/(?P<order_id>\d+)/$', consumers.OrderConsumer.as_asgi()),
]