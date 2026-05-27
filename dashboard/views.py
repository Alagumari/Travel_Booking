from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from tours.models import TourPackage, Review, Destination, TravelCategory
from payments.models import Payment
from accounts.models import UserProfile, Notification
import json


@login_required
def user_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'user'

    # Role பொறுத்து different dashboard
    if role == 'agent':
        return agent_dashboard(request)
    else:
        return regular_dashboard(request)


@login_required
def regular_dashboard(request):
    """Normal User Dashboard"""
    user = request.user
    bookings = Booking.objects.filter(user=user)
    total_spent = Payment.objects.filter(
        user=user, status='success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'role': 'user',
        'bookings': bookings[:5],
        'total_bookings': bookings.count(),
        'total_spent': total_spent,
        'upcoming_trips': bookings.filter(
            status='confirmed',
            travel_date__gte=timezone.now().date()
        ).count(),
        'wishlist_count': user.wishlist.count(),
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@login_required
def agent_dashboard(request):
    """Travel Agent Dashboard"""
    user = request.user

    # Agent-ஓட packages மட்டும்
    my_packages = TourPackage.objects.filter(agent=user)

    # Agent packages-ல வந்த bookings மட்டும்
    my_bookings = Booking.objects.filter(
        package__agent=user
    ).select_related('user', 'package')

    # Revenue — agent packages மட்டும்
    my_revenue = Payment.objects.filter(
        booking__package__agent=user,
        status='success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'role': 'agent',
        'my_packages': my_packages,
        'total_packages': my_packages.count(),
        'active_packages': my_packages.filter(is_active=True).count(),
        'my_bookings': my_bookings[:10],
        'total_bookings': my_bookings.count(),
        'my_revenue': my_revenue,
        'pending_bookings': my_bookings.filter(status='pending').count(),
    }
    return render(request, 'dashboard/agent_dashboard.html', context)

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related('package', 'payment')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'dashboard/booking_history.html', {'bookings': bookings, 'status_filter': status_filter})


@staff_member_required
def admin_dashboard(request):
    # Stats
    total_users = User.objects.filter(is_staff=False).count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
    active_tours = TourPackage.objects.filter(is_active=True).count()

    # Monthly revenue (last 6 months)
    monthly_data = []
    monthly_labels = []
    for i in range(5, -1, -1):
        d = timezone.now() - timedelta(days=30 * i)
        month_start = d.replace(day=1)
        if i > 0:
            next_month = (month_start + timedelta(days=32)).replace(day=1)
        else:
            next_month = timezone.now()
        rev = Payment.objects.filter(
            status='success',
            initiated_at__gte=month_start,
            initiated_at__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_data.append(float(rev))
        monthly_labels.append(d.strftime('%b %Y'))

    # Booking status breakdown
    booking_statuses = Booking.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'].capitalize() for s in booking_statuses]
    status_counts = [s['count'] for s in booking_statuses]

    # Top packages
    top_packages = TourPackage.objects.order_by('-booking_count')[:5]

    # Recent bookings
    recent_bookings = Booking.objects.select_related('user', 'package').order_by('-booked_at')[:10]

    # New users this month
    this_month = timezone.now().replace(day=1)
    new_users_this_month = User.objects.filter(date_joined__gte=this_month).count()

    context = {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'active_tours': active_tours,
        'monthly_data': json.dumps(monthly_data),
        'monthly_labels': json.dumps(monthly_labels),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'top_packages': top_packages,
        'recent_bookings': recent_bookings,
        'new_users_this_month': new_users_this_month,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@staff_member_required
def admin_users(request):
    users = User.objects.filter(is_staff=False).select_related('profile').order_by('-date_joined')
    search = request.GET.get('q', '')
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)
    return render(request, 'dashboard/admin_users.html', {'users': users, 'search': search})


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def is_agent_or_admin(user):
    
    if user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    return profile and profile.role in ['agent', 'admin']


@login_required
def admin_add_package(request):
    # Permission check
    if not is_agent_or_admin(request.user):
        raise PermissionDenied

    from tours.forms import PackageForm
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            pkg = form.save(commit=False)
            pkg.agent = request.user  
            pkg.save()
            images = request.FILES.getlist('images')
            from tours.models import PackageImage
            for i, img in enumerate(images):
                PackageImage.objects.create(
                    package=pkg, image=img,
                    order=i, is_primary=(i == 0)
                )
            from django.contrib import messages
            messages.success(request, 'Package added successfully!')

          
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role == 'agent':
                return redirect('user_dashboard')  # Agent dashboard
            return redirect('admin_packages')  # Admin page
    else:
        form = PackageForm()

    return render(request, 'dashboard/admin_package_form.html', {
        'form': form,
        'action': 'Add'
    })


@login_required
def admin_edit_package(request, pk):
    # Permission check
    if not is_agent_or_admin(request.user):
        raise PermissionDenied

    from tours.forms import PackageForm
    package = get_object_or_404(TourPackage, pk=pk)

    
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'agent':
        if package.agent != request.user:
            raise PermissionDenied  # வேற agent-ஓட package edit பண்ண முடியாது

    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Package updated successfully!')
            if profile and profile.role == 'agent':
                return redirect('user_dashboard')
            return redirect('admin_packages')
    else:
        form = PackageForm(instance=package)

    return render(request, 'dashboard/admin_package_form.html', {
        'form': form,
        'action': 'Edit',
        'package': package
    })

@login_required
def toggle_user_block(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.is_blocked = not profile.is_blocked
    profile.save()
    from django.contrib import messages
    status = 'blocked' if profile.is_blocked else 'unblocked'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_users')


@staff_member_required
def admin_bookings(request):
    bookings = Booking.objects.select_related('user', 'package').order_by('-booked_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'dashboard/admin_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter
    })


@staff_member_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'cancelled', 'completed', 'refunded']:
            booking.status = new_status
            booking.save()
            Notification.objects.create(
                user=booking.user,
                title='Booking Status Updated',
                message=f'Your booking {booking_id} status changed to {new_status.capitalize()}.',
                notif_type='booking'
            )
            from django.contrib import messages
            messages.success(request, f'Booking {booking_id} status updated to {new_status}.')
    return redirect('admin_bookings')


@staff_member_required
def admin_packages(request):
    packages = TourPackage.objects.select_related(
        'destination', 'category'
    ).order_by('-created_at')
    return render(request, 'dashboard/admin_packages.html', {'packages': packages})


@staff_member_required
def admin_delete_package(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    if request.method == 'POST':
        package.delete()
        from django.contrib import messages
        messages.success(request, 'Package deleted.')
    return redirect('admin_packages')