from django.contrib import admin
from .models import (
    Destination, TravelCategory, TourPackage,
    PackageImage, Itinerary, Review, Wishlist
)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_popular']
    list_filter = ['country', 'is_popular']
    search_fields = ['name', 'country']
    list_editable = ['is_popular']


@admin.register(TravelCategory)
class TravelCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 3
    fields = ['image', 'caption', 'is_primary', 'order']


class ItineraryInline(admin.TabularInline):
    model = Itinerary
    extra = 1
    fields = ['day_number', 'title', 'description', 'meals']


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'destination', 'category', 'price_per_person',
        'discount_percentage', 'duration_days', 'available_seats',
        'is_active', 'is_featured', 'is_bestseller', 'booking_count', 'avg_rating'
    ]
    list_filter = [
        'is_active', 'is_featured', 'is_bestseller',
        'category', 'transport_type', 'hotel_type'
    ]
    search_fields = ['title', 'destination__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'booking_count', 'avg_rating', 'review_count', 'package_id']
    list_editable = ['is_active', 'is_featured', 'is_bestseller', 'discount_percentage']
    inlines = [PackageImageInline, ItineraryInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('package_id', 'title', 'slug', 'destination', 'category', 'agent',
                       'short_description', 'description', 'highlights')
        }),
        ('Pricing', {
            'fields': ('price_per_person', 'discount_percentage', 'child_price')
        }),
        ('Duration & Details', {
            'fields': ('duration_days', 'duration_nights', 'hotel_type', 'hotel_details',
                       'transport_type', 'transport_details', 'food_details', 'difficulty')
        }),
        ('Availability', {
            'fields': ('total_seats', 'available_seats', 'start_date', 'end_date')
        }),
        ('Content', {
            'fields': ('inclusions', 'exclusions')
        }),
        ('Status & Flags', {
            'fields': ('is_active', 'is_featured', 'is_bestseller')
        }),
        ('Stats (Read-only)', {
            'fields': ('view_count', 'booking_count', 'avg_rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'rating', 'title', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified']
    search_fields = ['user__username', 'package__title', 'comment']
    list_editable = ['is_verified']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'added_at']
    search_fields = ['user__username', 'package__title']
