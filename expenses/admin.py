from django.contrib import admin

from .models import ExpenseCategory, Transaction


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "amount", "category", "date")
    list_filter = ("type", "category", "date")
    search_fields = ("title", "note")
    date_hierarchy = "date"
