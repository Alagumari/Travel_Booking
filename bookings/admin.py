from django.contrib import admin
from .models import Booking, TravelerDetail


class TravelerDetailInline(admin.TabularInline):
    model = TravelerDetail
    extra = 0
    fields = ['full_name', 'age', 'gender', 'passport_number', 'is_child']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_id', 'user', 'package', 'travel_date',
        'num_adults', 'num_children', 'total_amount', 'status', 'booked_at'
    ]
    list_filter = ['status', 'hotel_type', 'booked_at']
    search_fields = ['booking_id', 'user__username', 'package__title', 'contact_email']
    readonly_fields = ['booking_id', 'booked_at']
    list_editable = ['status']
    date_hierarchy = 'booked_at'
    inlines = [TravelerDetailInline]
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_id', 'user', 'package', 'status')
        }),
        ('Travel Details', {
            'fields': ('travel_date', 'num_adults', 'num_children', 'hotel_type')
        }),
        ('Pricing', {
            'fields': ('adult_price', 'child_price', 'discount_amount', 'total_amount')
        }),
        ('Contact', {
            'fields': ('contact_name', 'contact_email', 'contact_phone', 'special_requests')
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
