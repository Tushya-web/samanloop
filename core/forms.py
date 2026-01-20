from django import forms
from .models import Item

class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "name",
            "category",
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
