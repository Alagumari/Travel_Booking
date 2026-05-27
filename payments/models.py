from django.db import models
from django.contrib.auth.models import User
from bookings.models import Booking
import uuid


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
    ]

    payment_id = models.CharField(max_length=50, unique=True, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='razorpay')

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)

    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Refund
    refund_id = models.CharField(max_length=100, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refunded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-initiated_at']

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id} - {self.booking.booking_id} - {self.status}"
