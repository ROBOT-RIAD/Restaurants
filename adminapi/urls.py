from django.urls import path, include
from rest_framework.routers import DefaultRouter
from policy.views import PrivacyPolicyViewSet, TermsAndConditionsViewSet, FAQViewSet
from .views import RestaurantViewSet
router = DefaultRouter()

router.register('policy', PrivacyPolicyViewSet,basename="policy")
router.register(r'terms-and-conditions', TermsAndConditionsViewSet)
router.register(r'faq', FAQViewSet)
router.register(r'restaurants', RestaurantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
