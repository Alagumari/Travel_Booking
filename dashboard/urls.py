from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='dashboard'),
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('bookings/', views.booking_history, name='booking_history'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/toggle-block/', views.toggle_user_block, name='toggle_user_block'),
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/bookings/<str:booking_id>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('admin/packages/', views.admin_packages, name='admin_packages'),
    path('admin/packages/add/', views.admin_add_package, name='admin_add_package'),
    path('admin/packages/<int:pk>/edit/', views.admin_edit_package, name='admin_edit_package'),
    path('admin/packages/<int:pk>/delete/', views.admin_delete_package, name='admin_delete_package'),
]
