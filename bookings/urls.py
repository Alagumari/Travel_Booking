from django.urls import path
from . import views

urlpatterns = [
    path('book/<slug:slug>/', views.create_booking, name='create_booking'),
    path('confirmation/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('cancel/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('calculate-price/', views.calculate_price, name='calculate_price'),
]
