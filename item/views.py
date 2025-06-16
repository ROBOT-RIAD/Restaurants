from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Item
from .serializers import ItemSerializer
from accounts.permissions import IsOwnerRole,IsStaffRole,IsChefRole,IsCustomerRole
from .pagination import ItemPagination
from .filters import ItemFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from restaurant.models import Restaurant
from accounts.models import ChefStaff
from .permissions import IsStafforChefOfRestaurant
from device.models import Device
from rest_framework.exceptions import PermissionDenied
from order.models import Order
from rest_framework.decorators import action
from rest_framework.response import Response


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerRole]
    pagination_class = ItemPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ItemFilter
    search_fields = ['item_name', 'category__Category_name']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'owner':
            return Item.objects.filter(restaurant__owner=user)
        elif user.role in ['chef', 'staff']:
            restaurant_ids = ChefStaff.objects.filter(
                user=user,
                action='accepted'
            ).values_list('restaurant_id', flat=True)
            return Item.objects.filter(restaurant_id__in=restaurant_ids)
        return Item.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == 'owner':
            try:
                restaurant = Restaurant.objects.get(owner=user)
            except Restaurant.DoesNotExist:
                raise ValidationError("You do not own a restaurant.")
        elif user.role in ['chef', 'staff']:
            chef_staff = ChefStaff.objects.filter(
                user=user,
                action='accepted'
            ).first()
            if not chef_staff:
                raise ValidationError("You are not associated with any accepted restaurant.")
            restaurant = chef_staff.restaurant
        else:
            raise PermissionDenied("You are not authorized to add items.")

        serializer.save(restaurant=restaurant)

    def is_user_authorized(self, item):
        user = self.request.user
        if item.restaurant.owner == user:
            return True
        elif user.role in ['chef', 'staff']:
            return ChefStaff.objects.filter(
                user=user,
                restaurant=item.restaurant,
                action='accepted'
            ).exists()
        return False

    def perform_update(self, serializer):
        item = self.get_object()
        if not self.is_user_authorized(item):
            raise PermissionDenied("You don't have permission to update this item.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.is_user_authorized(instance):
            raise PermissionDenied("You don't have permission to delete this item.")
        instance.delete()



class StaffItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsStaffRole]
    serializer_class = ItemSerializer
    pagination_class = ItemPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ItemFilter
    search_fields = ['item_name', 'category__Category_name']

    def get_queryset(self):
        # Return only items from the restaurant the staff is assigned to
        try:
            chef_staff = ChefStaff.objects.get(user=self.request.user)
            return Item.objects.filter(restaurant=chef_staff.restaurant)
        except ChefStaff.DoesNotExist:
            return Item.objects.none()

    def perform_update(self, serializer):
        if not IsStafforChefOfRestaurant().has_object_permission(self.request, self, serializer.instance):
            raise PermissionDenied("You are not authorized to update this item.")
        serializer.save()

    def perform_destroy(self, instance):
        if not IsStafforChefOfRestaurant().has_object_permission(self.request, self, instance):
            raise PermissionDenied("You are not authorized to delete this item.")
        instance.delete()

    

    @action(detail=False,methods=['get'],url_path='status-summary')
    def status_summary(self,request):
        try:
            cheff_staff = ChefStaff.objects.get(user = request.user)
            restaurant = cheff_staff.restaurant
            available_items_count = Item.objects.filter(restaurant=restaurant,availability=True).count()
            preparing_order_count =  Order.objects.filter(restaurant= restaurant,status ='preparing').count()
            pending_order_count = Order.objects.filter(restaurant=restaurant, status='pending').count()
            return Response(
                {
                    "available_items_count": available_items_count,
                    "preparing_order_count": preparing_order_count,
                    "pending_order_count": pending_order_count
                }
            )
        except ChefStaff.DoesNotExist:
            return Response({
                "error": "Chef staff not found."
            }, status=403)





class ChefItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsChefRole]
    serializer_class = ItemSerializer
    pagination_class = ItemPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ItemFilter
    search_fields = ['item_name', 'category__Category_name']

    def get_queryset(self):
        # Return only items from the restaurant the staff is assigned to
        try:
            chef_staff = ChefStaff.objects.get(user=self.request.user)
            return Item.objects.filter(restaurant=chef_staff.restaurant)
        except ChefStaff.DoesNotExist:
            return Item.objects.none()

    def perform_update(self, serializer):
        if not IsStafforChefOfRestaurant().has_object_permission(self.request, self, serializer.instance):
            raise PermissionDenied("You are not authorized to update this item.")
        serializer.save()

    def perform_destroy(self, instance):
        if not IsStafforChefOfRestaurant().has_object_permission(self.request, self, instance):
            raise PermissionDenied("You are not authorized to delete this item.")
        instance.delete()

    
    @action(detail=False,methods=['get'],url_path='status-summary')
    def status_summary(self,request):
        try:
            cheff_staff = ChefStaff.objects.get(user = request.user)
            restaurant = cheff_staff.restaurant
            available_items_count = Item.objects.filter(restaurant=restaurant,availability=True).count()
            preparing_order_count =  Order.objects.filter(restaurant= restaurant,status ='preparing').count()
            pending_order_count = Order.objects.filter(restaurant=restaurant, status='pending').count()
            return Response(
                {
                    "available_items_count": available_items_count,
                    "preparing_order_count": preparing_order_count,
                    "pending_order_count": pending_order_count
                }
            )
        except ChefStaff.DoesNotExist:
            return Response({
                "error": "Chef staff not found."
            }, status=403)





class CustomerItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated,IsCustomerRole]
    pagination_class = ItemPagination  
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ItemFilter  
    search_fields = ['item_name', 'category__Category_name']

    def get_queryset(self):
        
        restaurant_ids = self.request.user.devices.values_list('restaurant_id', flat=True)
        print("Customer's restaurant IDs:", list(restaurant_ids))
        val=list(restaurant_ids)
        return Item.objects.filter(restaurant_id__in=val)










