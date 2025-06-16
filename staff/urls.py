from django.urls import path, include
from rest_framework.routers import DefaultRouter
from item.views import StaffItemViewSet
from order.views import ChefStaffOrdersAPIView, ChefStaffUpdateOrderStatusAPIView
from device.views import ReservationViewSet
router = DefaultRouter()
router.register('items', StaffItemViewSet, basename='staff-items')
router.register('reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
    path('orders/', ChefStaffOrdersAPIView.as_view(), name='staff-orders'),
    path('orders/<int:pk>/status/', ChefStaffUpdateOrderStatusAPIView.as_view(), name='staff-update-order-status'),
]