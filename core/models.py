from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager

from django.db import models
from django.contrib.auth.models import AbstractUser


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=10)

    city = models.CharField(max_length=28, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    profile = models.ImageField(upload_to="images/", null=True, blank=True)

    email_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    wallet_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    percentage_cut = models.DecimalField(max_digits=5, decimal_places=2, default=4.00)
    created_at = models.DateTimeField(auto_now_add=True)

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
        ("in use", "In Use")
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items"
    )
    
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_year = models.PositiveIntegerField()

    description = models.TextField(blank=True)

    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES)

    latitude = models.CharField(max_length=50, blank=True)
    longitude = models.CharField(max_length=50, blank=True)

    allow_delivery = models.BooleanField(default=False)
    self_pickup = models.BooleanField(default=True)

    city = models.CharField(max_length=100, blank=True, null=True)

    # 🔐 USER ACTUAL RENT PRICE ONLY
    rent_per_day = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    deposit_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )
    
    availability_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 AI calculation ONLY (not stored in DB)
    from decimal import Decimal
    from django.utils.timezone import now

    def calculate_rent(self):

        try:
            year = int(self.purchase_year)
        except:
            year = now().year

        age = max(0, now().year - year)

        age_factor = max(0.4, 1 - (age * 0.1))

        quality_factor = {
            "excellent": 1.0,
            "good": 0.85,
            "average": 0.7
        }.get(self.quality, 0.7)

        # 🔥 Category percentage
        category_percent = self.category.percentage_cut or Decimal("4.00")

        base_price = Decimal(self.purchase_price)

        suggested = (
            base_price *
            (category_percent / Decimal("100")) *
            Decimal(age_factor) *
            Decimal(quality_factor)
        )

        return round(suggested, 2)

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="items/")

class item_Request(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed")
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
class item_usage(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed")
    ]    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lent_items")
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rented_items")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=item_Request.STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
class payment(models.Model):
    item_usage = models.ForeignKey(item_usage, on_delete=models.CASCADE)
    payment_amt = models.DecimalField(max_digits=7, decimal_places=2)
    deposit = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    deposit_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    
class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

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
    
    
