from django.db import models
from django.utils.functional import cached_property
from decimal import Decimal
from djmoney.models.fields import MoneyField


class IngredientUnit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        help_text="Current amount in stock"
    )
    unit = models.ForeignKey(IngredientUnit, on_delete=models.PROTECT)
    cost_per_unit = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    @property
    def unit_display(self):
        return self.unit.name

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit_display})"

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    
    def calculate_cost(self):
            from djmoney.money import Money
            total = Money(0, 'USD') # Initialize as Money object
            for ri in self.recipe_ingredients.all():
                resolved = ri.resolved_ingredient
                if not resolved:
                    continue
                total += (ri.quantity * resolved.cost_per_unit)
            return total

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True, blank=True)
    ingredient_name = models.CharField(max_length=100, blank=True)
    ingredient_unit = models.ForeignKey(IngredientUnit, null=True, blank=True, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, help_text="Amount needed for this recipe")

    @cached_property
    def resolved_ingredient(self):
        if self.ingredient:
            return self.ingredient
        if not self.ingredient_name:
            return None
        return Ingredient.objects.filter(name__iexact=self.ingredient_name).first()

    @property
    def display_name(self):
        return self.ingredient.name if self.ingredient else self.ingredient_name

    @property
    def display_unit(self):
        resolved = self.resolved_ingredient
        if resolved:
            return resolved.unit_display
        return self.ingredient_unit.name if self.ingredient_unit else ''

    @property
    def missing_amount(self):
        resolved = self.resolved_ingredient
        if not resolved:
            return self.quantity
        if resolved.quantity >= self.quantity:
            return Decimal('0')
        return self.quantity - resolved.quantity

    @property
    def is_in_stock(self):
        return self.missing_amount == Decimal('0')

    def __str__(self):
        return f"{self.recipe.name} - {self.display_name}"
    
class Meal(models.Model):
    """A collection of recipes (e.g. Steak Dinner = Steak + Potatoes + Salad)"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # 1. ADD THIS FIELD:
    customer_price = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='USD', 
        null=True, 
        blank=True,
        help_text="Price displayed to customers"
    )
    
    def calculate_cost(self):
        from djmoney.money import Money
        total = Money(0, 'USD')
        for mr in self.meal_recipes.all():
            total += (mr.recipe.calculate_cost() * mr.quantity)
        return total

    def __str__(self):
        return f"{self.name} ({self.customer_price})"
    
    @property
    def projected_profit(self):
        from djmoney.money import Money
        # Use 0 if no price is set
        price = self.customer_price if self.customer_price else Money(0, 'USD')
        cost = self.calculate_cost()
        return price - cost

class MealRecipe(models.Model):
    """Links a Meal to a Recipe"""
    meal = models.ForeignKey(Meal, related_name='meal_recipes', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1.0, help_text="Servings of this recipe")

    def __str__(self):
        return f"{self.meal.name} -> {self.recipe.name}"