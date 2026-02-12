from django import forms
from .models import Item

from django import forms
from .models import User

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=60)
    email = forms.EmailField()
    phone = forms.CharField(max_length=10)
    password = forms.CharField(widget=forms.PasswordInput)

class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "name",
            # "category",
            "brand",
            "purchase_price",
            "purchase_year",
            "quality",
            "deposit_amount",
            "city",
        ]

        widgets = {
            "purchase_year": forms.NumberInput(attrs={"placeholder": "e.g. 2022"}),
            "deposit_amount": forms.NumberInput(attrs={"placeholder": "Optional"}),
        }
