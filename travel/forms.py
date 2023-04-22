from django import forms
from django.utils.translation import gettext_lazy as _
from .api import validate_amadeus_location
from django.urls import reverse_lazy

class FlightForm(forms.Form):
    
    ADULTS = [(i, i) for i in range(1, 6)]
    KIDS = [(i, i) for i in range(1, 6)]
    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business')
    ]

    from_location = forms.CharField(
        label='From', 
        max_length=100,
        validators=[validate_amadeus_location],
        error_messages={'invalid': 'Please enter an airport location.'},
        widget=forms.TextInput(attrs={'data-autocomplete-url': reverse_lazy('autocomplete'),'class': 'form-control', 'id':'id_from_location'})
    )
    to_location = forms.CharField(
        label='To', 
        max_length=100,
        validators=[validate_amadeus_location],
        error_messages={'invalid': 'Please enter an airport location.'},
        widget=forms.TextInput(attrs={'data-autocomplete-url': reverse_lazy('autocomplete'),'class': 'form-control', 'id':'id_to_location'})
    )
    departure_date = forms.DateField(
        label='Departure',
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date','placeholder':"From Date"})
    )
    return_date = forms.DateField(
        label='Return',
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date','placeholder':"To Date"})
    )
    adults = forms.ChoiceField(
        label='Adults', choices=ADULTS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    kids = forms.ChoiceField(
        label='Kids', choices=KIDS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_class = forms.ChoiceField(
        label='Class', choices=CLASS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
