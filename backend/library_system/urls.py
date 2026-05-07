from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/books/', include('apps.books.urls')),
    path('api/readers/', include('apps.readers.urls')),
    path('api/borrowings/', include('apps.borrowings.urls')),
    path('api/fines/', include('apps.fines.urls')),
    path('api/purchases/', include('apps.purchases.urls')),
    path('api/statistics/', include('apps.statistics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
