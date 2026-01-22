from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_menuweek_archive_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="menuitem",
            name="selling_price",
        ),
        migrations.RemoveField(
            model_name="menuitem",
            name="selling_price_currency",
        ),
    ]
