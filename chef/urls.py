from django.urls import path, include
from rest_framework.routers import DefaultRouter
from item.views import ChefItemViewSet
from order.views import ChefStaffOrdersAPIView, ChefStaffUpdateOrderStatusAPIView

router = DefaultRouter()
router.register('items', ChefItemViewSet, basename='chef-items')

urlpatterns = [
    path('', include(router.urls)),
    path('orders/', ChefStaffOrdersAPIView.as_view(), name='chef-orders'),
    path('orders/<int:pk>/status/', ChefStaffUpdateOrderStatusAPIView.as_view(), name='chef-update-order-status'),
]