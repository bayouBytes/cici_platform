import re
from django import forms
from django.forms import inlineformset_factory
from .models import Ingredient, Recipe, RecipeIngredient
from .models import Meal, MealRecipe
from djmoney.forms.widgets import MoneyWidget 

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit_type', 'unit_custom', 'cost_per_unit']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Flour'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'unit_type': forms.Select(attrs={'class': 'form-input'}),
            'unit_custom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Pinch, Clove, Bag'}),
            'cost_per_unit': MoneyWidget(attrs={'class': 'form-input', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cost_widget = self.fields['cost_per_unit'].widget
        if isinstance(cost_widget, MoneyWidget):
            cost_widget.widgets[0].attrs.update({
                'class': 'form-input pl-8',
                'inputmode': 'decimal',
                'style': 'padding-left: 2rem !important;',
            })
            cost_widget.widgets[1] = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        unit_type = cleaned_data.get('unit_type')
        unit_custom = cleaned_data.get('unit_custom', '')

        if unit_type == 'OTHER':
            if not unit_custom.strip():
                self.add_error('unit_custom', 'Enter a custom unit when using Other (custom).')
        else:
            cleaned_data['unit_custom'] = ''

        return cleaned_data

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'instructions']

RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient,
    fields=('ingredient', 'quantity'),
    extra=1, 
    can_delete=True
)

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'description', 'customer_price']
        
        widgets = {
             'name': forms.TextInput(attrs={'class': 'form-input'}),
             'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
             # We handle customer_price widget manually in the template now
        }

    def clean_name(self):
        """Force Title Case for the Meal Name"""
        name = self.cleaned_data.get('name')
        if name:
            return name.title() # "butTerY breAd" -> "Buttery Bread"
        return name

    def clean_description(self):
        """Force Sentence Case for Description"""
        description = self.cleaned_data.get('description')
        if description:
            # 1. Lowercase everything first to reset "LoADed" -> "loaded"
            description = description.lower()
            
            # 2. Capitalize the first letter of the whole text
            description = description[0].upper() + description[1:]
            
            # 3. Capitalize first letter after any punctuation (. ! ?) followed by space
            # Regex explanation: Find (. ! ?) followed by space, capture the next letter, uppercase it.
            def capitalize_match(match):
                return match.group().upper()
                
            p = re.compile(r'(?<=[\.\!\?]\s)\w')
            description = p.sub(capitalize_match, description)
            
            return description
        return description

MealRecipeFormSet = inlineformset_factory(
    Meal, MealRecipe,
    fields=('recipe', 'quantity'),
    extra=1,
    can_delete=True
)

