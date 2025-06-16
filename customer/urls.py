from django.urls import path, include
from category.views import CustomerCategoryListView
from rest_framework.routers import DefaultRouter
from item.views import CustomerItemViewSet
from order.views import OrderCreateAPIView, OrderCancelAPIView,MyOrdersAPIView,MySingleOrderAPIView
from review.views import CreateReviewAPIView
router = DefaultRouter()
router.register('items',CustomerItemViewSet, basename='customer_items')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CustomerCategoryListView.as_view(), name='customer-categories'),
    path('orders/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel'),
    path('uncomplete/orders/', MyOrdersAPIView.as_view(), name='my-orders'),
    path('uncomplete/orders/<int:pk>/', MySingleOrderAPIView.as_view(), name='my-single-order'),
    path('reviews/create/', CreateReviewAPIView.as_view(), name='create-review'),
]