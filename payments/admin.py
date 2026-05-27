from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'booking', 'user', 'amount',
        'currency', 'status', 'method', 'initiated_at'
    ]
    list_filter = ['status', 'method', 'currency']
    search_fields = ['payment_id', 'booking__booking_id', 'user__username', 'razorpay_payment_id']
    readonly_fields = ['payment_id', 'initiated_at']
    list_editable = ['status']
    date_hierarchy = 'initiated_at'
