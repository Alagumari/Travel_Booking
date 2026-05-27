from django.contrib import admin
from .models import UserProfile, Notification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'city', 'country', 'is_blocked', 'created_at']
    list_filter = ['role', 'is_blocked', 'email_verified']
    search_fields = ['user__username', 'user__email', 'phone']
    list_editable = ['is_blocked']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notif_type', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']
    search_fields = ['user__username', 'title']
