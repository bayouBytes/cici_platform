import re
from django import forms
from django.forms import inlineformset_factory
from .models import Ingredient, IngredientUnit, Recipe, RecipeIngredient
from .models import Meal, MealRecipe
from djmoney.forms.widgets import MoneyWidget 

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit', 'cost_per_unit']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Flour'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1', 'placeholder': 'e.g. 1'}),
            'unit': forms.Select(attrs={'class': 'form-input hidden'}),
            'cost_per_unit': MoneyWidget(attrs={'class': 'form-input', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = IngredientUnit.objects.all()
        if not self.instance or not self.instance.pk:
            self.fields['quantity'].initial = ''

        cost_widget = self.fields['cost_per_unit'].widget
        if isinstance(cost_widget, MoneyWidget):
            cost_widget.widgets[0].attrs.update({
                'class': 'form-input pl-8',
                'inputmode': 'decimal',
                'style': 'padding-left: 2rem !important;',
            })
            cost_widget.widgets[1] = forms.HiddenInput()


class IngredientUnitForm(forms.ModelForm):
    class Meta:
        model = IngredientUnit
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Pounds'}),
        }

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'instructions']

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'ingredient_name', 'ingredient_unit', 'quantity']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-input hidden'}),
            'ingredient_name': forms.HiddenInput(),
            'ingredient_unit': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].required = False
        self.fields['ingredient_name'].required = False
        self.fields['ingredient_unit'].required = False
        self.fields['ingredient'].queryset = Ingredient.objects.order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        ingredient = cleaned_data.get('ingredient')
        ingredient_name = (cleaned_data.get('ingredient_name') or '').strip()
        ingredient_unit = cleaned_data.get('ingredient_unit')

        if not ingredient and not ingredient_name:
            self.add_error('ingredient_name', 'Select or type an ingredient.')
        if ingredient and ingredient_name:
            cleaned_data['ingredient_name'] = ''
            cleaned_data['ingredient_unit'] = None
        if ingredient_name and not ingredient_unit:
            self.add_error('ingredient_unit', 'Select a unit for this ingredient.')

        return cleaned_data

RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient,
    form=RecipeIngredientForm,
    fields=('ingredient', 'ingredient_name', 'ingredient_unit', 'quantity'),
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

