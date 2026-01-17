from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'get_cost_display')

    def get_cost_display(self, obj):
        return f"${obj.calculate_cost():.2f}"
    get_cost_display.short_description = "Cost"

admin.site.register(Ingredient)