from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
import json

from .models import Booking
from tours.models import TourPackage
from .forms import BookingForm


# =========================
# CREATE BOOKING
# =========================
@login_required
def create_booking(request, slug):
    package = get_object_or_404(TourPackage, slug=slug, is_active=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            num_adults = form.cleaned_data['num_adults']
            num_children = form.cleaned_data['num_children']
            travel_date = form.cleaned_data['travel_date']
            hotel_type = form.cleaned_data['hotel_type']

            total_travelers = num_adults + num_children

            # Seat check
            if total_travelers > package.available_seats:
                messages.error(request, f'Only {package.available_seats} seats available.')
                return redirect('package_detail', slug=slug)

            # =========================
            # PRICE CALCULATION (DECIMAL SAFE)
            # =========================
            adult_price = package.discounted_price

            child_price = package.child_price
            if not child_price:
                child_price = adult_price * Decimal("0.7")

            total_amount = (Decimal(num_adults) * adult_price) + (Decimal(num_children) * child_price)

            # =========================
            # CREATE BOOKING
            # =========================
            booking = Booking.objects.create(
                user=request.user,
                package=package,
                num_adults=num_adults,
                num_children=num_children,
                travel_date=travel_date,
                hotel_type=hotel_type,
                adult_price=adult_price,
                child_price=child_price,
                total_amount=total_amount,
                contact_name=form.cleaned_data['contact_name'],
                contact_email=form.cleaned_data['contact_email'],
                contact_phone=form.cleaned_data['contact_phone'],
                special_requests=form.cleaned_data.get('special_requests', ''),
                status='pending',
            )

            # Reduce seats
            package.available_seats -= total_travelers
            package.booking_count += 1
            package.save(update_fields=['available_seats', 'booking_count'])

            return redirect('payment_initiate', booking_id=booking.booking_id)

        else:
            messages.error(request, 'Please fill all required fields.')

    else:
        form = BookingForm(initial={
            'contact_name': request.user.get_full_name() or request.user.username,
            'contact_email': request.user.email,
        })

    return render(request, 'bookings/create_booking.html', {
        'package': package,
        'form': form,
    })


# =========================
# BOOKING CONFIRMATION
# =========================
@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


# =========================
# CANCEL BOOKING
# =========================
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if not booking.is_cancellable:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('user_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('reason', '')

        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.cancelled_at = timezone.now()
        booking.save()

        # Restore seats
        booking.package.available_seats += booking.total_travelers
        booking.package.save(update_fields=['available_seats'])

        messages.success(
            request,
            f'Booking {booking_id} cancelled. Refund will be processed in 5-7 business days.'
        )
        return redirect('user_dashboard')

    return render(request, 'bookings/cancel_booking.html', {'booking': booking})


# =========================
# AJAX PRICE CALCULATION
# =========================
@login_required
def calculate_price(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        package_id = data.get('package_id')
        num_adults = int(data.get('num_adults', 1))
        num_children = int(data.get('num_children', 0))

        try:
            package = TourPackage.objects.get(id=package_id)

            adult_price = package.discounted_price

            child_price = package.child_price
            if not child_price:
                child_price = adult_price * Decimal("0.7")

            total = (Decimal(num_adults) * adult_price) + (Decimal(num_children) * child_price)

            return JsonResponse({
                'adult_price': float(adult_price),
                'child_price': float(child_price),
                'total': float(total),
                'available_seats': package.available_seats,
            })

        except TourPackage.DoesNotExist:
            return JsonResponse({'error': 'Package not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)