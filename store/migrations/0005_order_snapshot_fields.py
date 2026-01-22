from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_remove_menuitem_selling_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="customer_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="order",
            name="menu_week",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="orders",
                to="store.menuweek",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_cost",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_profit",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_price",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="line_cost",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="line_price",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="line_profit",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="meal_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="unit_cost",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="unit_price",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default=0, default_currency="USD", max_digits=14
            ),
        ),
    ]
