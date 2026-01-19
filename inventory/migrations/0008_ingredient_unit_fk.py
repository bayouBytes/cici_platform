from django.db import migrations, models
import django.db.models.deletion


def seed_units(apps, schema_editor):
    Ingredient = apps.get_model('inventory', 'Ingredient')
    IngredientUnit = apps.get_model('inventory', 'IngredientUnit')

    default_units = [
        'Pounds',
        'Ounces',
        'Grams',
        'Kilograms',
        'Milligrams',
        'Milliliters',
        'Liters',
        'Teaspoons',
        'Tablespoons',
        'Cups',
        'Pints',
        'Quarts',
        'Gallons',
        'Quantity/Count',
    ]

    for name in default_units:
        IngredientUnit.objects.get_or_create(name=name)

    for unit_name in (
        Ingredient.objects.filter(unit_type='OTHER')
        .exclude(unit_custom='')
        .values_list('unit_custom', flat=True)
        .distinct()
    ):
        cleaned = unit_name.strip()
        if cleaned:
            IngredientUnit.objects.get_or_create(name=cleaned)


def migrate_ingredient_units(apps, schema_editor):
    Ingredient = apps.get_model('inventory', 'Ingredient')
    IngredientUnit = apps.get_model('inventory', 'IngredientUnit')

    unit_type_to_name = {
        'LB': 'Pounds',
        'OZ': 'Ounces',
        'G': 'Grams',
        'KG': 'Kilograms',
        'MG': 'Milligrams',
        'ML': 'Milliliters',
        'L': 'Liters',
        'TSP': 'Teaspoons',
        'TBSP': 'Tablespoons',
        'CUP': 'Cups',
        'PT': 'Pints',
        'QT': 'Quarts',
        'GAL': 'Gallons',
        'QTY': 'Quantity/Count',
    }

    fallback_unit, _ = IngredientUnit.objects.get_or_create(name='Quantity/Count')

    for ingredient in Ingredient.objects.all():
        unit_name = None
        if ingredient.unit_type == 'OTHER':
            unit_name = (ingredient.unit_custom or '').strip()
        else:
            unit_name = unit_type_to_name.get(ingredient.unit_type)

        if unit_name:
            unit, _ = IngredientUnit.objects.get_or_create(name=unit_name)
        else:
            unit = fallback_unit

        ingredient.unit = unit
        ingredient.save(update_fields=['unit'])


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_ingredientunit'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='inventory.ingredientunit'),
        ),
        migrations.RunPython(seed_units, migrations.RunPython.noop),
        migrations.RunPython(migrate_ingredient_units, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.ingredientunit'),
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='unit_custom',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='unit_type',
        ),
    ]
