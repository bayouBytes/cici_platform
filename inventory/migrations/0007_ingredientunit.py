from django.db import migrations, models


def seed_custom_units(apps, schema_editor):
    Ingredient = apps.get_model('inventory', 'Ingredient')
    IngredientUnit = apps.get_model('inventory', 'IngredientUnit')

    seen = set()
    for unit_name in (
        Ingredient.objects.filter(unit_type='OTHER')
        .exclude(unit_custom='')
        .values_list('unit_custom', flat=True)
        .distinct()
    ):
        normalized = unit_name.strip().lower()
        if not normalized or normalized in seen:
            continue
        IngredientUnit.objects.get_or_create(name=unit_name.strip())
        seen.add(normalized)


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_ingredient_unit_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(seed_custom_units, migrations.RunPython.noop),
    ]
