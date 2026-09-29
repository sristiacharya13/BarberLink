from django import forms
from .models import Barber

class BarberForm(forms.ModelForm):
    class Meta:
        model=Barber
        fields='__all__'