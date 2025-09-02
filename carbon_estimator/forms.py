from django import forms
from .models import CarbonEntry

class CarbonEntryForm(forms.ModelForm):
    class Meta:
        model = CarbonEntry
        fields = ['transport_km', 'electricity_kwh', 'food_type', 'plastic_grams']
        widgets = {
            'transport_km': forms.NumberInput(attrs={'min': 0, 'step': 0.1, 'class': 'form-control'}),
            'electricity_kwh': forms.NumberInput(attrs={'min': 0, 'step': 0.1, 'class': 'form-control'}),
            'food_type': forms.Select(choices=[('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian'), ('mixed', 'Mixed')], attrs={'class': 'form-control'}),
            'plastic_grams': forms.NumberInput(attrs={'min': 0, 'step': 0.1, 'class': 'form-control'}),
        }
