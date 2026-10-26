from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ExpenseCategoryForm, TransactionFilterForm, TransactionForm
from .models import ExpenseCategory, Transaction


def dashboard(request):
    filter_form = TransactionFilterForm(request.GET or None)
    transactions = Transaction.objects.select_related("category")
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


def transaction_create(request):
    requested_type = request.GET.get("type")
    transaction_type = (
        requested_type if requested_type in Transaction.Type.values else None
    )
    initial = {"date": timezone.localdate()}
    if transaction_type:
        initial["type"] = transaction_type

    form = TransactionForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        transaction = form.save()
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
def transaction_delete(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    title = transaction.title
    transaction.delete()
    messages.success(request, f"“{title}” tranzaksiyasi o‘chirildi.")
    return redirect("dashboard")


def category_list(request):
    form = ExpenseCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"“{category.name}” kategoriyasi qo‘shildi.")
        return redirect("categories")

    return render(
        request,
        "expenses/categories.html",
        {"form": form, "categories": ExpenseCategory.objects.all()},
    )


@require_POST
def category_delete(request, category_id):
    category = get_object_or_404(ExpenseCategory, pk=category_id)
    if category.transactions.exists():
        messages.error(request, "Tranzaksiyalarda ishlatilayotgan kategoriyani o‘chirib bo‘lmaydi.")
    else:
        name = category.name
        category.delete()
        messages.success(request, f"“{name}” kategoriyasi o‘chirildi.")
    return redirect("categories")
