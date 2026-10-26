from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import ExpenseCategory, Transaction


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Login"
        self.fields["username"].help_text = (
            "Harf, raqam va @/./+/-/_ belgilaridan foydalaning."
        )
        self.fields["password1"].label = "Parol"
        self.fields["password1"].help_text = (
            "Kamida 8 belgi bo‘lsin va faqat raqamlardan iborat bo‘lmasin."
        )
        self.fields["password2"].label = "Parolni tasdiqlash"
        self.fields["password2"].help_text = "Parolni qaytadan kiriting."


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["title", "amount", "type", "category", "date", "note"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Masalan, Oylik maosh"}),
            "amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "type": forms.Select(),
            "category": forms.Select(),
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "Ixtiyoriy izoh"}),
        }
        labels = {
            "title": "Nomi",
            "amount": "Summa (so‘m)",
            "type": "Tranzaksiya turi",
            "category": "Xarajat kategoriyasi",
            "date": "Sana",
            "note": "Izoh",
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = ExpenseCategory.objects.filter(
            user=user
        ).order_by("name")
        self.fields["category"].required = False
        self.fields["date"].input_formats = ["%Y-%m-%d"]
        transaction_type = self.data.get("type") or self.initial.get("type")
        if transaction_type == Transaction.Type.INCOME:
            self.fields["title"].widget.attrs["placeholder"] = "Masalan, Ish haqi"
            self.fields["note"].widget.attrs["placeholder"] = (
                "Masalan, Bugun ish haqimni oldim"
            )
        elif transaction_type == Transaction.Type.EXPENSE:
            self.fields["title"].widget.attrs["placeholder"] = (
                "Masalan, Pol ta’miri"
            )
            self.fields["note"].widget.attrs["placeholder"] = (
                "Masalan, Polga material oldim"
            )

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("type")
        category = cleaned_data.get("category")

        if transaction_type == Transaction.Type.EXPENSE and category is None:
            self.add_error("category", "Chiqim uchun kategoriyani tanlang.")
        elif transaction_type == Transaction.Type.INCOME:
            cleaned_data["category"] = None

        return cleaned_data


class TransactionFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Boshlanish sanasi",
    )
    end_date = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Tugash sanasi",
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=ExpenseCategory.objects.none(),
        label="Kategoriya",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = ExpenseCategory.objects.filter(
            user=user
        ).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            self.add_error("end_date", "Tugash sanasi boshlanish sanasidan oldin bo‘lishi mumkin emas.")
        return cleaned_data


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name", "color"]
        labels = {"name": "Kategoriya nomi", "color": "Rang"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Masalan, Oziq-ovqat"}),
            "color": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data["name"]
        categories = ExpenseCategory.objects.filter(user=self.user, name__iexact=name)
        if self.instance.pk:
            categories = categories.exclude(pk=self.instance.pk)
        if categories.exists():
            raise forms.ValidationError("Bu kategoriya nomi allaqachon mavjud.")
        return name
