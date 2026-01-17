from django.db import models
from decimal import Decimal
from djmoney.models.fields import MoneyField
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('LB', 'Pounds'),
        ('OZ', 'Ounces'),
        ('G', 'Grams'),
        ('QTY', 'Quantity/Count'),
    ]
    
    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=5, choices=UNIT_CHOICES)
    cost_per_unit = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    def __str__(self):
        return f"{self.name} (${self.cost_per_unit}/{self.unit_type})"

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    
    def calculate_cost(self):
            from djmoney.money import Money
            total = Money(0, 'USD') # Initialize as Money object
            for ri in self.recipe_ingredients.all():
                total += (ri.quantity * ri.ingredient.cost_per_unit)
            return total

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, help_text="Amount needed for this recipe")

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"
    
class Meal(models.Model):
    """A collection of recipes (e.g. Steak Dinner = Steak + Potatoes + Salad)"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def calculate_cost(self):
        from djmoney.money import Money
        total = Money(0, 'USD')
        for mr in self.meal_recipes.all():
            # Cost = Recipe Cost * Quantity (e.g. 1 serving)
            total += (mr.recipe.calculate_cost() * mr.quantity)
        return total

    def __str__(self):
        return self.name

class MealRecipe(models.Model):
    """Links a Meal to a Recipe"""
    meal = models.ForeignKey(Meal, related_name='meal_recipes', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1.0, help_text="Servings of this recipe")

    def __str__(self):
        return f"{self.meal.name} -> {self.recipe.name}"