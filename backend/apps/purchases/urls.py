from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseSuggestionViewSet, PurchaseOrderViewSet

router = DefaultRouter()
router.register(r'suggestions', PurchaseSuggestionViewSet, basename='suggestion')
router.register(r'orders', PurchaseOrderViewSet, basename='purchase-order')

urlpatterns = [
    path('', include(router.urls)),
]
