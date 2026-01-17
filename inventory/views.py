from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

# CORRECT: Import Meal from local models (Inventory), NOT Store
from .models import Ingredient, Recipe, Meal
from store.models import MenuItem, MenuWeek

from .forms import IngredientForm, RecipeForm, RecipeIngredientFormSet, MealForm, MealRecipeFormSet
from store.forms import MenuItemForm 

  
@staff_member_required
def chef_dashboard(request):
    """The main command center for the Chef."""
    active_week = MenuWeek.objects.filter(is_active=True).first()
    
    context = {
        'ingredients': Ingredient.objects.all(),
        'recipes': Recipe.objects.all(),
        'menu_items': MenuItem.objects.filter(menu_week=active_week) if active_week else [],
        'active_week': active_week,
        # Pass empty forms for the 'Add' modals
        'ingredient_form': IngredientForm(),
        'menu_item_form': MenuItemForm(initial={'menu_week': active_week}),
        'meals': Meal.objects.all(),
    }
    return render(request, 'inventory/dashboard.html', context)

@staff_member_required
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('chef_dashboard')

@staff_member_required
def manage_recipe(request, recipe_id=None):
    """
    Handles both creating NEW recipes and EDITING existing ones.
    This is a dedicated page because recipe logic is complex.
    """
    if recipe_id:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        title = f"Edit {recipe.name}"
    else:
        recipe = Recipe()
        title = "Create New Recipe"

    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        
        if form.is_valid() and formset.is_valid():
            saved_recipe = form.save()
            formset.save()
            return redirect('chef_dashboard')
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

    return render(request, 'inventory/recipe_editor.html', {
        'form': form,
        'formset': formset,
        'title': title
    })

@staff_member_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    return redirect('chef_dashboard')

@staff_member_required
def manage_meal(request, meal_id=None):
    """Creates or Edits a Meal (Collection of Recipes)"""
    if meal_id:
        meal = get_object_or_404(Meal, id=meal_id)
        title = f"Edit {meal.name}"
    else:
        meal = Meal()
        title = "Create New Meal"

    if request.method == 'POST':
        form = MealForm(request.POST, instance=meal)
        formset = MealRecipeFormSet(request.POST, instance=meal)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('chef_dashboard')
    else:
        form = MealForm(instance=meal)
        formset = MealRecipeFormSet(instance=meal)

    return render(request, 'inventory/meal_editor.html', {
        'form': form,
        'formset': formset,
        'title': title
    })

@staff_member_required
def delete_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    meal.delete()
    return redirect('chef_dashboard')