from django.urls import path
from . import views

urlpatterns = [
    path('pay/<str:booking_id>/', views.initiate_payment, name='payment_initiate'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/<str:booking_id>/', views.payment_success, name='payment_success'),
    path('failed/<str:booking_id>/', views.payment_failed, name='payment_failed'),
    path('ticket/<str:booking_id>/', views.download_ticket, name='download_ticket'),
    path('qr/<str:booking_id>/', views.generate_qr, name='generate_qr'),
]
