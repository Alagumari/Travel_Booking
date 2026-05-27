from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import TourPackage, Destination, TravelCategory, Review, Wishlist, PackageImage, Itinerary
from .forms import ReviewForm, PackageSearchForm


def home(request):
    featured_packages = TourPackage.objects.filter(is_active=True, is_featured=True)[:6]
    bestseller_packages = TourPackage.objects.filter(is_active=True, is_bestseller=True)[:4]
    popular_destinations = Destination.objects.filter(is_popular=True)[:6]
    categories = TravelCategory.objects.all()
    recent_packages = TourPackage.objects.filter(is_active=True).order_by('-created_at')[:8]
    top_rated = TourPackage.objects.filter(is_active=True, avg_rating__gte=4).order_by('-avg_rating')[:4]

    context = {
        'featured_packages': featured_packages,
        'bestseller_packages': bestseller_packages,
        'popular_destinations': popular_destinations,
        'categories': categories,
        'recent_packages': recent_packages,
        'top_rated': top_rated,
    }
    return render(request, 'tours/home.html', context)


def package_list(request):
    packages = TourPackage.objects.filter(is_active=True)
    categories = TravelCategory.objects.all()
    destinations = Destination.objects.all()

    # Search
    search_query = request.GET.get('q', '')
    destination = request.GET.get('destination', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_days = request.GET.get('min_days', '')
    max_days = request.GET.get('max_days', '')
    sort_by = request.GET.get('sort', '-created_at')

    if search_query:
        packages = packages.filter(
            Q(title__icontains=search_query) |
            Q(destination__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if destination:
        packages = packages.filter(destination__id=destination)
    if category:
        packages = packages.filter(category__slug=category)
    if min_price:
        packages = packages.filter(price_per_person__gte=min_price)
    if max_price:
        packages = packages.filter(price_per_person__lte=max_price)
    if min_days:
        packages = packages.filter(duration_days__gte=min_days)
    if max_days:
        packages = packages.filter(duration_days__lte=max_days)

    sort_options = {
        'price_asc': 'price_per_person',
        'price_desc': '-price_per_person',
        'rating': '-avg_rating',
        'popular': '-booking_count',
        'newest': '-created_at',
        'duration_asc': 'duration_days',
    }
    packages = packages.order_by(sort_options.get(sort_by, '-created_at'))

    paginator = Paginator(packages, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'destinations': destinations,
        'search_query': search_query,
        'selected_destination': destination,
        'selected_category': category,
        'sort_by': sort_by,
        'total_count': packages.count(),
    }
    return render(request, 'tours/package_list.html', context)


def package_detail(request, slug):
    package = get_object_or_404(TourPackage, slug=slug, is_active=True)
    package.view_count += 1
    package.save(update_fields=['view_count'])

    images = package.images.all()
    itinerary = package.itinerary.all()
    reviews = package.reviews.all().order_by('-created_at')
    related_packages = TourPackage.objects.filter(
        destination=package.destination, is_active=True
    ).exclude(id=package.id)[:4]

    user_review = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_review = Review.objects.filter(package=package, user=request.user).first()
        in_wishlist = Wishlist.objects.filter(user=request.user, package=package).exists()

    # Rating breakdown
    rating_breakdown = {}
    for i in range(1, 6):
        rating_breakdown[i] = reviews.filter(rating=i).count()

    context = {
        'package': package,
        'images': images,
        'itinerary': itinerary,
        'reviews': reviews,
        'related_packages': related_packages,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
        'rating_breakdown': rating_breakdown,
        'review_form': ReviewForm(instance=user_review) if user_review else ReviewForm(),
    }
    return render(request, 'tours/package_detail.html', context)


@login_required
def add_review(request, slug):
    package = get_object_or_404(TourPackage, slug=slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        existing = Review.objects.filter(package=package, user=request.user).first()
        if existing:
            form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.package = package
            review.user = request.user
            review.save()
            # Update package average rating
            avg = Review.objects.filter(package=package).aggregate(Avg('rating'))['rating__avg'] or 0
            package.avg_rating = round(avg, 1)
            package.review_count = Review.objects.filter(package=package).count()
            package.save(update_fields=['avg_rating', 'review_count'])
            messages.success(request, 'Your review has been submitted!')
        else:
            messages.error(request, 'Error submitting review.')
    return redirect('package_detail', slug=slug)


@login_required
def toggle_wishlist(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, package=package)
    if not created:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from wishlist'})
    return JsonResponse({'status': 'added', 'message': 'Added to wishlist'})


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('package')
    return render(request, 'tours/wishlist.html', {'wishlist_items': wishlist_items})


def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    packages = TourPackage.objects.filter(destination=destination, is_active=True)
    return render(request, 'tours/destination_detail.html', {
        'destination': destination,
        'packages': packages,
    })
