from rest_framework import serializers
from .models import Device, Reservation


class DeviceSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.resturent_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Device
        fields = ['id', 'table_name', 'restaurant', 'action','restaurant_name','username']
        read_only_fields =['username', 'restaurant_name','restaurant']



class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'




class ReservationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['status']