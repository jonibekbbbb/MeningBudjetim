from django.db import migrations


DEFAULT_CATEGORIES = [
    ("Oziq-ovqat", "#4caf93"),
    ("Transport", "#f2a65a"),
    ("Ta’lim", "#6c63ff"),
    ("Kiyim-kechak", "#e879a9"),
    ("Uy-joy", "#4d9de0"),
    ("Sog‘liq", "#e76f51"),
    ("Boshqa", "#8d99ae"),
]


def create_default_categories(apps, schema_editor):
    ExpenseCategory = apps.get_model("expenses", "ExpenseCategory")
    ExpenseCategory.objects.using(schema_editor.connection.alias).bulk_create(
        [
            ExpenseCategory(name=name, color=color)
            for name, color in DEFAULT_CATEGORIES
        ],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [("expenses", "0001_initial")]

    operations = [
        migrations.RunPython(
            create_default_categories,
            reverse_code=migrations.RunPython.noop,
        )
    ]
