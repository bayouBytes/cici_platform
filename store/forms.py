from django import forms
from .models import MenuItem

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['recipe', 'selling_price', 'menu_week']
        widgets = {
            'selling_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.50'}),
        }