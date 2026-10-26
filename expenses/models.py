from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Kategoriya nomi")
    color = models.CharField(
        max_length=7,
        default="#6c63ff",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Rang #RRGGBB ko‘rinishida bo‘lishi kerak.",
            )
        ],
        verbose_name="Rang",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Xarajat kategoriyasi"
        verbose_name_plural = "Xarajat kategoriyalari"

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME = "income", "Kirim"
        EXPENSE = "expense", "Chiqim"

    title = models.CharField(max_length=120, verbose_name="Nomi")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(9999999999.99)],
        verbose_name="Summa",
    )
    type = models.CharField(
        max_length=7,
        choices=Type.choices,
        verbose_name="Turi",
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="transactions",
        null=True,
        blank=True,
        verbose_name="Kategoriya",
    )
    date = models.DateField(default=timezone.localdate, verbose_name="Sana")
    note = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Tranzaksiya"
        verbose_name_plural = "Tranzaksiyalar"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="transaction_amount_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(type__in=["income", "expense"]),
                name="transaction_type_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_type_display()}: {self.title} ({self.amount})"
