from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class Destination(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, {self.country}"


class TravelCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='bi-globe')
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TourPackage(models.Model):

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    ]

    HOTEL_TYPE_CHOICES = [
        ('budget', 'Budget (2★)'),
        ('standard', 'Standard (3★)'),
        ('deluxe', 'Deluxe (4★)'),
        ('luxury', 'Luxury (5★)'),
    ]

    TRANSPORT_CHOICES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('cruise', 'Cruise'),
        ('self_drive', 'Self Drive'),
    ]

    package_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, max_length=350)

    destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        related_name='packages'
    )

    category = models.ForeignKey(
        TravelCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='packages'
    )

    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='packages'
    )

    description = models.TextField()
    short_description = models.CharField(max_length=500)
    highlights = models.TextField(help_text='One highlight per line')

    # Pricing
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    child_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Duration
    duration_days = models.PositiveIntegerField()
    duration_nights = models.PositiveIntegerField()

    # Details
    hotel_type = models.CharField(max_length=20, choices=HOTEL_TYPE_CHOICES, default='standard')
    hotel_details = models.TextField(blank=True)
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default='flight')
    transport_details = models.TextField(blank=True)
    food_details = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')

    # Availability
    total_seats = models.PositiveIntegerField(default=20)
    available_seats = models.PositiveIntegerField(default=20)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Inclusions / Exclusions
    inclusions = models.TextField(blank=True)
    exclusions = models.TextField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    # Stats
    view_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)

    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    review_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while TourPackage.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # ✅ FIXED (NO FLOAT ERROR)
    @property
    def discounted_price(self):
        price = self.price_per_person
        discount = Decimal(self.discount_percentage) / Decimal('100')
        return price * (Decimal('1') - discount)

    @property
    def savings(self):
        return self.price_per_person - self.discounted_price

    def get_highlights_list(self):
        return [h.strip() for h in self.highlights.split('\n') if h.strip()]

    def get_inclusions_list(self):
        return [i.strip() for i in self.inclusions.split('\n') if i.strip()]

    def get_exclusions_list(self):
        return [e.strip() for e in self.exclusions.split('\n') if e.strip()]


class PackageImage(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='packages/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.package.title} - Image {self.order}"


class Itinerary(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='itinerary')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    accommodation = models.CharField(max_length=200, blank=True)
    meals = models.CharField(max_length=100, blank=True)
    activities = models.TextField(blank=True)

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


class Review(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    travel_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['package', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.package.title}"

    def get_star_range(self):
        return range(self.rating)

    def get_empty_star_range(self):
        return range(5 - self.rating)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'package']

    def __str__(self):
        return f"{self.user.username} - {self.package.title}"