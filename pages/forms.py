from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'arrival_date',
            'departure_date',
            'number_of_adults',
            'number_of_children',
            'special_requests',
            'first_name',
            'last_name',
            'nationality',
            'booking_number',
            'email',
            'phone',
        ]