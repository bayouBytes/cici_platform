from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_recipeingredient_inverse'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeingredient',
            name='ingredient_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='inventory.ingredientunit'),
        ),
    ]
