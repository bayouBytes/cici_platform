from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

# CORRECT: Import Meal from local models (Inventory), NOT Store
from .models import Ingredient, IngredientUnit, Recipe, Meal
from store.models import MenuItem, MenuWeek

from .forms import (
    IngredientForm,
    IngredientUnitForm,
    RecipeForm,
    RecipeIngredientFormSet,
    MealForm,
    MealRecipeFormSet,
)
from store.forms import MenuItemForm 
from djmoney.money import Money

  
@staff_member_required
def chef_dashboard(request):
    """The main command center for the Chef."""
    active_week = MenuWeek.objects.filter(is_active=True).first()
    ingredients = Ingredient.objects.all()
    ingredient_total_value = Money(0, 'USD')
    for ingredient in ingredients:
        ingredient_total_value += ingredient.quantity * ingredient.cost_per_unit
    
    context = {
        'ingredients': ingredients,
        'recipes': Recipe.objects.all(),
        'menu_items': MenuItem.objects.filter(menu_week=active_week) if active_week else [],
        'active_week': active_week,
        # Pass empty forms for the 'Add' modals
        'ingredient_form': IngredientForm(),
        'edit_ingredient_form': IngredientForm(prefix='edit'),
        'unit_form': IngredientUnitForm(prefix='unit'),
        'edit_unit_form': IngredientUnitForm(prefix='unit-edit'),
        'units': IngredientUnit.objects.all(),
        'menu_item_form': MenuItemForm(initial={'menu_week': active_week}),
        'meals': Meal.objects.all(),
        'ingredient_total_value': ingredient_total_value,
    }
    return render(request, 'inventory/dashboard.html', context)

@staff_member_required
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': ingredient.id,
                    'name': ingredient.name,
                    'unit': ingredient.unit.name,
                    'cost_per_unit_amount': str(ingredient.cost_per_unit.amount),
                })
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            print(form.errors)  # Add this to see why it failed in your console
    return redirect('chef_dashboard')

@staff_member_required
def edit_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient, prefix='edit')
        if form.is_valid():
            form.save()
    return redirect('chef_dashboard')

@staff_member_required
def delete_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    ingredient.delete()
    return redirect('chef_dashboard')

@staff_member_required
def delete_ingredient_unit(request, unit_id):
    unit = get_object_or_404(IngredientUnit, id=unit_id)
    if Ingredient.objects.filter(unit=unit).exists():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unit is in use.'}, status=400)
        return redirect('chef_dashboard')
    unit.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'id': unit_id})
    return redirect('chef_dashboard')

@staff_member_required
def add_ingredient_unit(request):
    if request.method == 'POST':
        form = IngredientUnitForm(request.POST, prefix='unit')
        if form.is_valid():
            unit = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'id': unit.id, 'name': unit.name})
        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
    return redirect('chef_dashboard')

@staff_member_required
def edit_ingredient_unit(request, unit_id):
    unit = get_object_or_404(IngredientUnit, id=unit_id)
    if request.method == 'POST':
        form = IngredientUnitForm(request.POST, instance=unit, prefix='unit-edit')
        if form.is_valid():
            unit = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'id': unit.id, 'name': unit.name})
        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
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
        'title': title,
        'ingredients': Ingredient.objects.order_by('name'),
        'units': IngredientUnit.objects.order_by('name'),
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

    recipe_costs = {
        recipe.id: str(recipe.calculate_cost().amount)
        for recipe in Recipe.objects.order_by('name')
    }
    total_cost = meal.calculate_cost() if meal_id else None

    return render(request, 'inventory/meal_editor.html', {
        'form': form,
        'formset': formset,
        'title': title,
        'recipe_costs': recipe_costs,
        'total_cost': total_cost,
    })

@staff_member_required
def delete_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    meal.delete()
    return redirect('chef_dashboard')