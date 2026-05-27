from django import forms
from .models import Review, TourPackage, Itinerary, PackageImage


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'travel_date']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Review title'}),
        }


class PackageSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    destination = forms.CharField(required=False)
    category = forms.CharField(required=False)
    min_price = forms.IntegerField(required=False, min_value=0)
    max_price = forms.IntegerField(required=False, min_value=0)
    min_days = forms.IntegerField(required=False, min_value=1)
    max_days = forms.IntegerField(required=False, min_value=1)


class PackageForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        exclude = ['slug', 'package_id', 'avg_rating', 'review_count', 'view_count', 'booking_count']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'highlights': forms.Textarea(attrs={'rows': 4}),
            'inclusions': forms.Textarea(attrs={'rows': 4}),
            'exclusions': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ItineraryForm(forms.ModelForm):
    class Meta:
        model = Itinerary
        fields = ['day_number', 'title', 'description', 'accommodation', 'meals', 'activities']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'activities': forms.Textarea(attrs={'rows': 3}),
        }
