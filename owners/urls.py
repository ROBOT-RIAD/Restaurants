from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurant.views import OwnerRegisterView
from category.views import CategoryViewSet
from item.views import ItemViewSet,MostSellingItemsAPIView
from accounts.views import ChefStaffViewSet
from device.views import DeviceViewSet,ReservationViewSet
from order.views import OwnerRestaurantOrdersAPIView,OwnerUpdateOrderStatusAPIView,OrderAnalyticsAPIView
from review.views import OwnerRestaurantReviewListAPIView
from device.views import DeviceViewSetall



router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('items', ItemViewSet, basename='item')
router.register('chef-staff', ChefStaffViewSet, basename='chef-staff')
router.register('devices', DeviceViewSet, basename='device')
router.register('reservations', ReservationViewSet, basename='reservation')
router.register('devicesall', DeviceViewSetall, basename='deviceall')

urlpatterns = [
    path('', include(router.urls)),
    path('register/',OwnerRegisterView.as_view(),name='ownerRegister'),
    path('orders/', OwnerRestaurantOrdersAPIView.as_view(), name='owner-orders'),
    path('orders/status/<int:pk>/', OwnerUpdateOrderStatusAPIView.as_view(), name='update-order-status'),
    path('reviews/', OwnerRestaurantReviewListAPIView.as_view(), name='owner-reviews'),
    path('most-selling-items/', MostSellingItemsAPIView.as_view(), name='most-selling-items'),
    path('orders/analytics/', OrderAnalyticsAPIView.as_view(), name='owner-order-analytics')
]
