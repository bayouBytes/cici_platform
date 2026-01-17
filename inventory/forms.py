from django import forms
from django.forms import inlineformset_factory
from .models import Ingredient, Recipe, RecipeIngredient
from .models import Meal, MealRecipe

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'unit_type', 'cost_per_unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Flour'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'instructions']

# This formset allows us to edit multiple ingredients for a recipe at once
RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient,
    fields=('ingredient', 'quantity'),
    extra=1, # Show 1 empty row by default
    can_delete=True
)

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'description']

# Allows adding multiple Recipes to a Meal
MealRecipeFormSet = inlineformset_factory(
    Meal, MealRecipe,
    fields=('recipe', 'quantity'),
    extra=1,
    can_delete=True
)

