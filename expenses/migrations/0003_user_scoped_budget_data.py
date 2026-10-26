from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_existing_records_to_owner(apps, schema_editor):
    ExpenseCategory = apps.get_model("expenses", "ExpenseCategory")
    Transaction = apps.get_model("expenses", "Transaction")
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    database = schema_editor.connection.alias

    if not (
        ExpenseCategory.objects.using(database).exists()
        or Transaction.objects.using(database).exists()
    ):
        return

    owner = User.objects.using(database).filter(is_superuser=True).order_by("pk").first()
    if owner is None:
        username = "legacy-budget-owner"
        suffix = 1
        while User.objects.using(database).filter(username=username).exists():
            username = f"legacy-budget-owner-{suffix}"
            suffix += 1
        owner = User.objects.using(database).create(username=username, is_active=False)
        owner.password = "!"
        owner.save(using=database, update_fields=["password"])

    ExpenseCategory.objects.using(database).all().update(user_id=owner.pk)
    Transaction.objects.using(database).all().update(user_id=owner.pk)


class Migration(migrations.Migration):
    dependencies = [
        ("expenses", "0002_seed_default_categories"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="expensecategory",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expense_categories",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AlterField(
            model_name="expensecategory",
            name="name",
            field=models.CharField(max_length=50, verbose_name="Kategoriya nomi"),
        ),
        migrations.RunPython(
            assign_existing_records_to_owner,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="expensecategory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expense_categories",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AddConstraint(
            model_name="expensecategory",
            constraint=models.UniqueConstraint(
                fields=("user", "name"),
                name="unique_category_name_per_user",
            ),
        ),
    ]
