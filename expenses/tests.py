from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TransactionForm
from .models import ExpenseCategory, Transaction


class TransactionFormTests(TestCase):
    def setUp(self):
        self.category, _ = ExpenseCategory.objects.get_or_create(
            name="Oziq-ovqat", defaults={"color": "#22aa88"}
        )

    def test_expense_requires_category(self):
        form = TransactionForm(
            data={
                "title": "Tushlik",
                "amount": "25000",
                "type": Transaction.Type.EXPENSE,
                "date": "2026-10-24",
                "category": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_income_does_not_keep_expense_category(self):
        form = TransactionForm(
            data={
                "title": "Oylik",
                "amount": "5000000",
                "type": Transaction.Type.INCOME,
                "date": "2026-10-24",
                "category": str(self.category.pk),
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["category"])


class DashboardTests(TestCase):
    def setUp(self):
        self.food, _ = ExpenseCategory.objects.get_or_create(
            name="Oziq-ovqat", defaults={"color": "#22aa88"}
        )
        self.transport, _ = ExpenseCategory.objects.get_or_create(
            name="Transport", defaults={"color": "#ee8844"}
        )
        Transaction.objects.create(
            title="Oylik",
            amount=Decimal("5000000"),
            type=Transaction.Type.INCOME,
            date=date(2026, 10, 1),
        )
        Transaction.objects.create(
            title="Bozor",
            amount=Decimal("250000"),
            type=Transaction.Type.EXPENSE,
            category=self.food,
            date=date(2026, 10, 10),
        )
        Transaction.objects.create(
            title="Avtobus",
            amount=Decimal("50000"),
            type=Transaction.Type.EXPENSE,
            category=self.transport,
            date=date(2026, 9, 20),
        )

    def test_dashboard_shows_totals_and_balance(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_income"], Decimal("5000000"))
        self.assertEqual(response.context["total_expenses"], Decimal("300000"))
        self.assertEqual(response.context["balance"], Decimal("4700000"))

    def test_dashboard_renders_category_chart_without_javascript(self):
        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, 'role="progressbar"')
        self.assertEqual(
            [row["width_percent"] for row in response.context["chart_data"]],
            [Decimal("100"), Decimal("20")],
        )
        self.assertNotContains(response, "<script")

    def test_date_filter_limits_transactions_and_totals(self):
        response = self.client.get(
            reverse("dashboard"),
            {"start_date": "2026-10-01", "end_date": "2026-10-31"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_expenses"], Decimal("250000"))
        self.assertEqual(response.context["transactions"].count(), 2)

    def test_category_filter_limits_expense_chart_and_totals(self):
        response = self.client.get(
            reverse("dashboard"),
            {"category": str(self.food.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_expenses"], Decimal("250000"))
        self.assertEqual(response.context["transactions"].count(), 1)

    def test_invalid_date_range_is_reported(self):
        response = self.client.get(
            reverse("dashboard"),
            {"start_date": "2026-10-31", "end_date": "2026-10-01"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("end_date", response.context["filter_form"].errors)

    def test_transaction_delete_requires_post(self):
        transaction = Transaction.objects.get(title="Bozor")

        response = self.client.get(
            reverse("transaction_delete", args=[transaction.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Transaction.objects.filter(pk=transaction.pk).exists())

    def test_transaction_can_be_deleted(self):
        transaction = Transaction.objects.get(title="Bozor")

        response = self.client.post(
            reverse("transaction_delete", args=[transaction.pk])
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(Transaction.objects.filter(pk=transaction.pk).exists())

    def test_expense_can_be_created(self):
        response = self.client.post(
            reverse("transaction_create"),
            {
                "title": "Kitob",
                "amount": "80000",
                "type": Transaction.Type.EXPENSE,
                "category": str(self.food.pk),
                "date": "2026-10-24",
                "note": "Dars uchun",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(Transaction.objects.filter(title="Kitob").exists())

    def test_expense_without_category_is_rejected(self):
        response = self.client.post(
            reverse("transaction_create"),
            {
                "title": "Tushlik",
                "amount": "25000",
                "type": Transaction.Type.EXPENSE,
                "category": "",
                "date": "2026-10-24",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("category", response.context["form"].errors)
        self.assertFalse(Transaction.objects.filter(title="Tushlik").exists())

    def test_income_quick_add_defaults_to_today(self):
        response = self.client.get(
            reverse("transaction_create"),
            {"type": Transaction.Type.INCOME},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial["date"],
            timezone.localdate(),
        )
        self.assertEqual(
            response.context["form"].initial["type"],
            Transaction.Type.INCOME,
        )
        self.assertContains(response, "Bugungi kirimni qo‘shish")
        self.assertContains(
            response,
            f'value="{timezone.localdate().isoformat()}"',
        )

    def test_expense_quick_add_defaults_to_today(self):
        response = self.client.get(
            reverse("transaction_create"),
            {"type": Transaction.Type.EXPENSE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial["date"],
            timezone.localdate(),
        )
        self.assertEqual(
            response.context["form"].initial["type"],
            Transaction.Type.EXPENSE,
        )
        self.assertContains(response, "Bugungi chiqimni qo‘shish")
        self.assertContains(
            response,
            f'value="{timezone.localdate().isoformat()}"',
        )


class CategoryTests(TestCase):
    def test_category_can_be_created(self):
        response = self.client.post(
            reverse("categories"),
            {"name": "Qo‘shimcha", "color": "#336699"},
        )

        self.assertRedirects(response, reverse("categories"))
        self.assertTrue(ExpenseCategory.objects.filter(name="Qo‘shimcha").exists())

    def test_category_in_use_cannot_be_deleted(self):
        category = ExpenseCategory.objects.create(name="Sinov transport")
        Transaction.objects.create(
            title="Metro",
            amount=Decimal("15000"),
            type=Transaction.Type.EXPENSE,
            category=category,
            date=date(2026, 10, 24),
        )

        response = self.client.post(
            reverse("category_delete", args=[category.pk])
        )

        self.assertRedirects(response, reverse("categories"))
        self.assertTrue(ExpenseCategory.objects.filter(pk=category.pk).exists())
