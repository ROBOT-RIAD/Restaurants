# views.py
from rest_framework import viewsets, permissions,generics
from .models import Category, Restaurant
from .serializers import CategorySerializer,CustomerCategorySerializer
from rest_framework.exceptions import ValidationError, PermissionDenied
from accounts.permissions import IsOwnerRole,IsCustomerRole




class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated,IsOwnerRole]

    def get_queryset(self):
        # Limit to categories owned by the current user (owner)
        return Category.objects.filter(restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        try:
            restaurant = Restaurant.objects.get(owner=self.request.user)
        except Restaurant.DoesNotExist:
            raise ValidationError("You don't have a restaurant yet.")

        serializer.save(restaurant=restaurant)

    def perform_update(self, serializer):
        category = self.get_object()
        if category.restaurant.owner != self.request.user:
            raise PermissionDenied("You don't have permission to edit this category.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.restaurant.owner != self.request.user:
            raise PermissionDenied("You don't have permission to delete this category.")
        instance.delete()





class CustomerCategoryListView(generics.ListAPIView):
    serializer_class = CustomerCategorySerializer
    permission_classes = [permissions.IsAuthenticated,IsCustomerRole]

    def get_queryset(self):
        user = self.request.user

        # Only allow customers
        if user.role != 'customer':
            raise PermissionDenied("Only customers can access this endpoint.")

        # Find restaurant via Device model
        device = user.devices.first()
        if not device or not device.restaurant:
            raise PermissionDenied("No restaurant associated with this customer device.")

        return Category.objects.filter(restaurant=device.restaurant)
