from rest_framework import generics, status,filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .pagination import TenPerPagePagination
from .models import Order
from .serializers import OrderCreateSerializer, OrderDetailSerializer
from accounts.permissions import IsCustomerRole,IsOwnerRole,IsChefOrStaff
from accounts.models import ChefStaff

# date 
from datetime import date
from django.db.models import Sum

class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated,IsCustomerRole]

    def perform_create(self, serializer):
        device = self.request.user.devices.first()  # Assuming 1 device per user
        serializer.save(device=device, restaurant=device.restaurant)

class OrderCancelAPIView(APIView):
    permission_classes = [IsAuthenticated,IsCustomerRole]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, device__user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response({"error": "Only pending orders can be cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()
        return Response({"message": "Order cancelled successfully"})
    

class MyOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated,IsCustomerRole]
    pagination_class = TenPerPagePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['id']

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            device__user=user,
            status__in=['pending', 'preparing', 'served']
        ).order_by('-created_time')


class MySingleOrderAPIView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated,IsCustomerRole]
    lookup_field = 'pk' 

    def get_queryset(self):
        return Order.objects.filter(
            device__user=self.request.user,
            status__in=['pending', 'preparing', 'served']
        )
    


class OwnerRestaurantOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated,IsOwnerRole]
    pagination_class = TenPerPagePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['id']

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(restaurant__owner=user).order_by('-created_time')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        today = date.today()
        completed_orders = queryset.filter(status='completed')
        completed_today = completed_orders.filter(updated_time__date=today)

        stats = {
            "total_completed_orders": completed_orders.count(),
            "today_completed_order_price": str(completed_today.aggregate(total=Sum('total_price'))['total'] or 0),
            "ongoing_orders": queryset.filter(status__in=['pending', 'preparing', 'served']).count()
        }

        return self.get_paginated_response({
            "stats": stats,
            "orders": serializer.data
        })
    



class OwnerUpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated,IsOwnerRole]

    def patch(self, request, pk):
        user = request.user
        try:
            order = Order.objects.get(pk=pk, restaurant__owner=user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in dict(Order._meta.get_field('status').choices):
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({"message": "Order status updated", "status": order.status})
    



class ChefStaffOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated,IsChefOrStaff]
    pagination_class = TenPerPagePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['id']

    def get_queryset(self):
        user = self.request.user
        # Get all restaurants where user is active staff/chef
        restaurant_ids = ChefStaff.objects.filter(user=user, action='active').values_list('restaurant_id', flat=True)
        return Order.objects.filter(restaurant_id__in=restaurant_ids).order_by('-created_time')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Paginate results
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        # Calculate stats
        ongoing_statuses = ['pending', 'preparing', 'served']
        total_ongoing = queryset.filter(status__in=ongoing_statuses).count()
        total_completed = queryset.filter(status='completed').count()

        stats = {
            "total_ongoing_orders": total_ongoing,
            "total_completed_orders": total_completed,
        }

        return self.get_paginated_response({
            "stats": stats,
            "orders": serializer.data
        })



class ChefStaffUpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated,IsChefOrStaff]

    def patch(self, request, pk):
        user = request.user
        new_status = request.data.get('status')

        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        is_chef = ChefStaff.objects.filter(user=user, restaurant=order.restaurant, action='active').exists()
        if not is_chef:
            return Response({"detail": "You are not authorized to update this order."}, status=status.HTTP_403_FORBIDDEN)

        order.status = new_status
        order.save()
        return Response({"detail": f"Order status updated to {new_status}"}, status=status.HTTP_200_OK)