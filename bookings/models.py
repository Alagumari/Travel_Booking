from django.db import models
from django.contrib.auth.models import User
from tours.models import TourPackage
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]
    HOTEL_TYPE_CHOICES = [
        ('budget', 'Budget (2★)'),
        ('standard', 'Standard (3★)'),
        ('deluxe', 'Deluxe (4★)'),
        ('luxury', 'Luxury (5★)'),
    ]

    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='bookings')

    # Traveler info
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    travel_date = models.DateField()
    hotel_type = models.CharField(max_length=20, choices=HOTEL_TYPE_CHOICES, default='standard')

    # Pricing
    adult_price = models.DecimalField(max_digits=10, decimal_places=2)
    child_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Contact
    contact_name = models.CharField(max_length=200)
    contact_email = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=15)
    special_requests = models.TextField(blank=True)

    # Timestamps
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Cancellation
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-booked_at']

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"TXP{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.user.username} - {self.package.title}"

    @property
    def total_travelers(self):
        return self.num_adults + self.num_children

    @property
    def is_cancellable(self):
        from django.utils import timezone
        import datetime
        if self.status in ['cancelled', 'refunded', 'completed']:
            return False
        days_until_travel = (self.travel_date - timezone.now().date()).days
        return days_until_travel > 3


class TravelerDetail(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='travelers')
    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    passport_number = models.CharField(max_length=20, blank=True)
    is_child = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.booking.booking_id}"
