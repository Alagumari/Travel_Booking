"""TravelX Pro URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tours import views as tour_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tour_views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('tours/', include('tours.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
