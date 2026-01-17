import re
from django import forms
from django.forms import inlineformset_factory
from .models import Ingredient, Recipe, RecipeIngredient
from .models import Meal, MealRecipe
from djmoney.forms.widgets import MoneyWidget 

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit_type', 'cost_per_unit']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Flour'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
        }

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

