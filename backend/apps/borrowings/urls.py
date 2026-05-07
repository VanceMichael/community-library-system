from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r'borrowings', BorrowingViewSet, basename='borrowing')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]
