from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.listings.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('favorites/', include('apps.favorites.urls')),
    path('reports/', include('apps.reports.urls')),
    path('ads/', include('apps.advertisements.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)