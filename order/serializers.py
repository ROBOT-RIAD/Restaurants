from rest_framework import serializers
from .models import Order, OrderItem
from item.models import Item

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']

class OrderCreateSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['device', 'restaurant', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        total = 0
        for item_data in order_items_data:
            item = item_data['item']
            quantity = item_data['quantity']
            OrderItem.objects.create(order=order, item=item, quantity=quantity, price=item.price)
            total += item.price * quantity
        order.total_price = total
        order.save()
        return order

class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Order
        fields = '__all__'
