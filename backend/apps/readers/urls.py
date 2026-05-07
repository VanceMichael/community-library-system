from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReaderViewSet

router = DefaultRouter()
router.register(r'', ReaderViewSet, basename='reader')

urlpatterns = [
    path('', include(router.urls)),
]
