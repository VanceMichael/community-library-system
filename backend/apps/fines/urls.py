from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FineViewSet, OverdueReminderViewSet

router = DefaultRouter()
router.register(r'fines', FineViewSet, basename='fine')
router.register(r'reminders', OverdueReminderViewSet, basename='reminder')

urlpatterns = [
    path('', include(router.urls)),
]
