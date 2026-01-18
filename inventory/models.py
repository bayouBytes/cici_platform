from django.db import models
from decimal import Decimal
from djmoney.models.fields import MoneyField
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('LB', 'Pounds'),
        ('OZ', 'Ounces'),
        ('G', 'Grams'),
        ('KG', 'Kilograms'),
        ('MG', 'Milligrams'),
        ('ML', 'Milliliters'),
        ('L', 'Liters'),
        ('TSP', 'Teaspoons'),
        ('TBSP', 'Tablespoons'),
        ('CUP', 'Cups'),
        ('PT', 'Pints'),
        ('QT', 'Quarts'),
        ('GAL', 'Gallons'),
        ('QTY', 'Quantity/Count'),
        ('OTHER', 'Other (custom)'),
    ]
    
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        help_text="Current amount in stock"
    )
    unit_type = models.CharField(max_length=5, choices=UNIT_CHOICES)
    unit_custom = models.CharField(
        max_length=50,
        blank=True,
        help_text="Custom unit label when using Other (custom)."
    )
    cost_per_unit = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    @property
    def unit_display(self):
        if self.unit_type == 'OTHER' and self.unit_custom:
            return self.unit_custom
        return dict(self.UNIT_CHOICES).get(self.unit_type, self.unit_type)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit_display})"

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