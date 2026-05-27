from django.urls import path
from . import views

urlpatterns = [
    path('', views.package_list, name='package_list'),

    # ✅ STATIC URLS FIRST
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:package_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),

    path('<slug:slug>/review/', views.add_review, name='add_review'),

    # ✅ ALWAYS LAST (IMPORTANT)
    path('<slug:slug>/', views.package_detail, name='package_detail'),
]