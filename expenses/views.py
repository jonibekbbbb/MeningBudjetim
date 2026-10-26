from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    ExpenseCategoryForm,
    RegistrationForm,
    TransactionFilterForm,
    TransactionForm,
)
from .models import ExpenseCategory, Transaction

DEFAULT_CATEGORIES = [
    ("Oziq-ovqat", "#4caf93"),
    ("Transport", "#f2a65a"),
    ("Ta’lim", "#6c63ff"),
    ("Kiyim-kechak", "#e879a9"),
    ("Uy-joy", "#4d9de0"),
    ("Sog‘liq", "#e76f51"),
    ("Boshqa", "#8d99ae"),
]


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with db_transaction.atomic():
            user = form.save()
            ExpenseCategory.objects.bulk_create(
                [
                    ExpenseCategory(user=user, name=name, color=color)
                    for name, color in DEFAULT_CATEGORIES
                ]
            )
        login(request, user)
        messages.success(request, "Hisobingiz yaratildi. Xush kelibsiz!")
        return redirect("dashboard")

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    filter_form = TransactionFilterForm(request.GET or None, user=request.user)
    transactions = Transaction.objects.filter(user=request.user).select_related(
        "category"
    )
    filter_is_valid = filter_form.is_valid()

    if filter_is_valid:
        filters = filter_form.cleaned_data
        if filters["start_date"]:
            transactions = transactions.filter(date__gte=filters["start_date"])
        if filters["end_date"]:
            transactions = transactions.filter(date__lte=filters["end_date"])
        if filters["category"]:
            transactions = transactions.filter(category=filters["category"])

    totals = transactions.aggregate(
        income=Sum("amount", filter=Q(type=Transaction.Type.INCOME)),
        expenses=Sum("amount", filter=Q(type=Transaction.Type.EXPENSE)),
    )
    total_income = totals["income"] or 0
    total_expenses = totals["expenses"] or 0
    category_totals = (
        transactions.filter(type=Transaction.Type.EXPENSE, category__isnull=False)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    )
    chart_data = list(category_totals)
    largest_category_total = max(
        (row["total"] for row in chart_data),
        default=0,
    )
    for row in chart_data:
        row["name"] = row.pop("category__name")
        row["color"] = row.pop("category__color")
        row["width_percent"] = (
            row["total"] * 100 / largest_category_total
            if largest_category_total
            else 0
        )

    return render(
        request,
        "expenses/dashboard.html",
        {
            "transactions": transactions,
            "filter_form": filter_form,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses,
            "chart_data": chart_data,
        },
    )


@login_required
def transaction_create(request):
    requested_type = request.GET.get("type")
    transaction_type = (
        requested_type if requested_type in Transaction.Type.values else None
    )
    initial = {"date": timezone.localdate()}
    if transaction_type:
        initial["type"] = transaction_type

    form = TransactionForm(request.POST or None, initial=initial, user=request.user)
    if request.method == "POST" and form.is_valid():
        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.save()
        messages.success(request, f"“{transaction.title}” tranzaksiyasi saqlandi.")
        return redirect("dashboard")

    page_title = "Tranzaksiya qo‘shish"
    if transaction_type == Transaction.Type.INCOME:
        page_title = "Bugungi kirimni qo‘shish"
    elif transaction_type == Transaction.Type.EXPENSE:
        page_title = "Bugungi chiqimni qo‘shish"

    return render(
        request,
        "expenses/transaction_form.html",
        {"form": form, "page_title": page_title},
    )


@require_POST
@login_required
def transaction_delete(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        pk=transaction_id,
        user=request.user,
    )
    title = transaction.title
    transaction.delete()
    messages.success(request, f"“{title}” tranzaksiyasi o‘chirildi.")
    return redirect("dashboard")


@login_required
def category_list(request):
    form = ExpenseCategoryForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        category.save()
        messages.success(request, f"“{category.name}” kategoriyasi qo‘shildi.")
        return redirect("categories")

    return render(
        request,
        "expenses/categories.html",
        {
            "form": form,
            "categories": ExpenseCategory.objects.filter(user=request.user),
        },
    )


@require_POST
@login_required
def category_delete(request, category_id):
    category = get_object_or_404(
        ExpenseCategory,
        pk=category_id,
        user=request.user,
    )
    if category.transactions.exists():
        messages.error(request, "Tranzaksiyalarda ishlatilayotgan kategoriyani o‘chirib bo‘lmaydi.")
    else:
        name = category.name
        category.delete()
        messages.success(request, f"“{name}” kategoriyasi o‘chirildi.")
    return redirect("categories")
