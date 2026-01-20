from django.db import models

from django.db import models
from django.conf import settings
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):

    QUALITY_CHOICES = [
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("average", "Average"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("borrowed", "Borrowed"),
        ("maintenance", "Under Maintenance"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    brand = models.CharField(max_length=120)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_year = models.PositiveIntegerField()
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES)

    suggested_rent_per_day = models.DecimalField(
        max_digits=8, decimal_places=2, editable=False
    )

    deposit_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    city = models.CharField(max_length=100)
    availability_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # -------- SMART PRICE CALCULATION -------- #
    def calculate_rent(self):
        age = max(0, now().year - self.purchase_year)
        age_factor = max(0.4, 1 - (age * 0.1))

        quality_factor = {
            "excellent": 1.0,
            "good": 0.85,
            "average": 0.7
        }.get(self.quality, 0.7)

        return round(
            float(self.purchase_price) * 0.015 *
            age_factor * quality_factor,
            2
        )

    def save(self, *args, **kwargs):
        self.suggested_rent_per_day = self.calculate_rent()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="items/")


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    held_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} Wallet"


class WalletTransaction(models.Model):

    TRANSACTION_TYPE = [
        ("credit", "Credit"),
        ("debit", "Debit"),
        ("hold", "Deposit Hold"),
        ("release", "Deposit Release"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.transaction_type} - ₹{self.amount}"