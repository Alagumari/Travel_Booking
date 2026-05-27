from django import forms
from .models import Booking
from django.utils import timezone


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'num_adults', 'num_children', 'travel_date',
            'hotel_type', 'contact_name', 'contact_email',
            'contact_phone', 'special_requests'
        ]
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requirements...'}),
            'contact_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
        }

    def clean_travel_date(self):
        date = self.cleaned_data.get('travel_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Travel date cannot be in the past.")
        return date

    def clean_num_adults(self):
        n = self.cleaned_data.get('num_adults')
        if n < 1:
            raise forms.ValidationError("At least 1 adult is required.")
        return n
