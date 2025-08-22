from rest_framework import generics, status,filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .pagination import TenPerPagePagination
from .models import Order
from .serializers import OrderCreateSerializer, OrderDetailSerializer
from accounts.permissions import IsCustomerRole,IsOwnerRole,IsChefOrStaff
from accounts.models import ChefStaff
from django.utils.timezone import now
from django.db.models import Sum, Count
from calendar import month_name
from restaurant.models import Restaurant
from accounts.models import ChefStaff

# date 
from datetime import date,timedelta
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
        queryset = self.filter_queryset(self.get_queryset())  # ✅ apply search filtering

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        # Stats should be calculated on the FULL (unfiltered) queryset
        full_queryset = self.get_queryset()
        today = date.today()
        completed_orders = full_queryset.filter(status='completed')
        completed_today = completed_orders.filter(updated_time__date=today)

        stats = {
            "total_completed_orders": completed_orders.count(),
            "today_completed_order_count": completed_today.count(),
            "ongoing_orders": full_queryset.filter(status__in=['pending', 'preparing', 'served']).count()
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
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        full_queryset = self.get_queryset()
        ongoing_statuses = ['pending', 'preparing', 'served']
        total_ongoing = full_queryset.filter(status__in=ongoing_statuses).count()
        total_completed = full_queryset.filter(status='completed').count()

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
    


class OrderAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerRole]

    def get(self, request):
        user = request.user
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        this_year = today.year
        last_year = this_year - 1

        restaurants = Restaurant.objects.filter(owner=user)

        # Get all orders for owner's restaurant
        orders = Order.objects.filter(restaurant__in=restaurants)

        # Filter completed orders
        completed_orders = orders.filter(status='completed')

        # ---- TODAY COMPLETED ORDER PRICE ----
        today_total_price = (
            completed_orders.filter(updated_time__date=today)
            .aggregate(total=Sum('total_price'))['total'] or 0
        )

        # ---- WEEKLY GROWTH (compare this week vs last week) ----
        last_week_start = start_of_week - timedelta(days=7)
        last_week_end = start_of_week - timedelta(days=1)

        this_week_total = (
            completed_orders.filter(updated_time__date__gte=start_of_week)
            .aggregate(total=Sum('total_price'))['total'] or 0
        )
        last_week_total = (
            completed_orders.filter(updated_time__date__range=[last_week_start, last_week_end])
            .aggregate(total=Sum('total_price'))['total'] or 0
        )

        weekly_growth = 0
        if last_week_total > 0:
            weekly_growth = ((this_week_total - last_week_total) / last_week_total) * 100

        # ---- Monthly Data for Current Year ----
        current_year_data = {month.lower()[:3]: 0 for month in month_name if month}
        last_year_data = {month.lower()[:3]: 0 for month in month_name if month}

        for order in completed_orders:
            month = order.updated_time.month
            year = order.updated_time.year

            if year == this_year:
                key = month_name[month].lower()[:3]
                current_year_data[key] += 1
            elif year == last_year:
                key = month_name[month].lower()[:3]
                last_year_data[key] += 1

        total_member = ChefStaff.objects.filter(restaurant__in=restaurants).count()

        return Response({
            "status": {
                "today_total_completed_order_price": str(today_total_price),
                "weekly_growth": round(weekly_growth, 2),
                "total_member": total_member,
                "current_year": this_year,
                "last_year": last_year

            },
            "current_year": current_year_data,
            "last_year": last_year_data
        })