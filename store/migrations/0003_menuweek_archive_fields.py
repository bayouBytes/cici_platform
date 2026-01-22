from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_menuitem_meal"),
    ]

    operations = [
        migrations.AddField(
            model_name="menuweek",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="menuweek",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
