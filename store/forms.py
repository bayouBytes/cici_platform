from django import forms
from .models import MenuItem, MenuWeek
from inventory.models import Meal

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['meal', 'menu_week']
        widgets = {
            'menu_week': forms.HiddenInput(),
            'meal': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal'].queryset = Meal.objects.order_by('name')
        self.fields['meal'].required = True


class MenuWeekForm(forms.ModelForm):
    class Meta:
        model = MenuWeek
        fields = ['name', 'start_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Week of Feb 10'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }