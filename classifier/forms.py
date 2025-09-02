# classifier/forms.py
from django import forms
from .models import WasteImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = WasteImage
        fields = ['image']
