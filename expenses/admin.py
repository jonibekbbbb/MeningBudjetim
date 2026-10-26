from django.contrib import admin

from .models import ExpenseCategory, Transaction


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "color")
    search_fields = ("name",)
    list_filter = ("user",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "type", "amount", "category", "date")
    list_filter = ("type", "category", "date")
    search_fields = ("title", "note")
    date_hierarchy = "date"
