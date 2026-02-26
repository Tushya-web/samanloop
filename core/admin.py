from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
import csv

from .models import (
    User, Category, Item, ItemImage,
    item_Request, item_usage, Payment,
    Review, Query, Wallet, WalletTransaction
)

def get_status_color(status):
    colors = {
        "available": "#10b981",
        "active": "#10b981",
        "accepted": "#10b981",
        "pending": "#f59e0b",
        "in use": "#f59e0b",
        "rejected": "#ef4444",
        "blocked": "#ef4444",
        "completed": "#3b82f6",
    }
    return colors.get(status.lower(), "#64748b")

from django.contrib.admin import AdminSite
from django.utils.timezone import now
from django.db.models import Sum
from .models import User, Item, item_Request, Payment

class SamanLoopAdminSite(AdminSite):
    site_header = "SamanLoop Command Center"
    site_title = "SamanLoop Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):

        total_users = User.objects.count()
        total_items = Item.objects.count()

        total_revenue = Payment.objects.aggregate(
            total=Sum("payment_amt")
        )["total"] or 0

        pending_requests = item_Request.objects.filter(
            status="pending"
        ).count()

        recent_users = User.objects.order_by("-created")[:5]

        active_items_count = Item.objects.filter(
            availability_status="available"
        ).count()

        if total_items > 0:
            availability_rate = round(
                (active_items_count / total_items) * 100
            )
        else:
            availability_rate = 0

        extra_context = extra_context or {}
        extra_context.update({
            "total_users": total_users,
            "total_items": total_items,
            "total_revenue": total_revenue,
            "pending_requests": pending_requests,
            "recent_users": recent_users,
            "availability_rate": availability_rate,
            "active_items_count": active_items_count,
            "now": now().strftime("%d %b %Y"),
        })

        return super().index(request, extra_context=extra_context)

admin_site = SamanLoopAdminSite(name="samanloop_admin")

# @admin.register(User)

class UserAdmin(admin.ModelAdmin):

    list_display = (
        "avatar_display",
        "name",
        "email",
        "city",
        "wallet_status",
        "verified_badge",
        "active_badge",
    )

    list_filter = ("email_verified", "is_blocked", "city")
    search_fields = ("name", "email", "phone_number")
    actions = ["mark_verified", "block_users", "export_csv"]

    def avatar_display(self, obj):
        return format_html(
            '<img src="https://ui-avatars.com/api/?name={}&background=random" '
            'style="width:30px;height:30px;border-radius:50%;" />',
            obj.name
        )
    avatar_display.short_description = ""

    def wallet_status(self, obj):
        return format_html(
            '<b style="color:#0d9488;">₹{}</b>',
            obj.wallet_balance
        )

    def verified_badge(self, obj):
        return obj.email_verified
    verified_badge.boolean = True
    verified_badge.short_description = "Verified"

    def active_badge(self, obj):
        color = "#10b981" if not obj.is_blocked else "#ef4444"
        text = "Active" if not obj.is_blocked else "Blocked"
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:12px; font-size:10px;">{}</span>',
            color, text
        )

    @admin.action(description="Mark as Email Verified")
    def mark_verified(self, request, queryset):
        queryset.update(email_verified=True)

    @admin.action(description="Block Selected Users")
    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)

    @admin.action(description="Export to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="SamanLoop_Users.csv"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Phone", "Wallet", "Verified"])
        for u in queryset:
            writer.writerow([
                u.name,
                u.email,
                u.phone_number,
                u.wallet_balance,
                u.email_verified
            ])
        return response


# ==========================
# ITEM IMAGE INLINE
# ==========================

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1


# ==========================
# ITEM ADMIN
# ==========================

# @admin.register(Item)

class ItemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "owner_link",
        "rent_display",
        "status_badge",
        "created_at",
    )

    list_filter = ("category", "availability_status", "quality")
    search_fields = ("name", "brand", "owner__email")
    inlines = [ItemImageInline]

    def owner_link(self, obj):
        url = reverse("admin:core_user_change", args=[obj.owner.id])
        return format_html('<a href="{}">{}</a>', url, obj.owner.name)

    def rent_display(self, obj):
        return format_html(
            '<b>₹{}</b> <small>/day</small>',
            obj.rent_per_day
        )

    def status_badge(self, obj):
        return format_html(
            '<span style="color:{}; font-weight:bold;">● {}</span>',
            get_status_color(obj.availability_status),
            obj.availability_status.upper()
        )


# ==========================
# RENTAL REQUEST ADMIN
# ==========================

# @admin.register(item_Request)
class ItemRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "item",
        "renter",
        "total_rent",
        "status_badge",
        "created_at",
    )

    list_filter = ("status",)

    def status_badge(self, obj):
        return format_html(
            '<span style="background:{}; color:white; padding:4px 12px; '
            'border-radius:20px; font-size:11px; font-weight:bold;">{}</span>',
            get_status_color(obj.status),
            obj.status.upper()
        )

from decimal import Decimal
from django.db import transaction

# @admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "borrower",
        "lender",
        "payment_amt",
        "deposit",
        "deposit_state_badge",
        "dispute_badge",
        "payment_date",
    )

    list_filter = ("deposit_state", "payment_date")
    search_fields = ("borrower__email", "lender__email")

    actions = [
        "resolve_full_refund",
        "resolve_give_lender",
        "resolve_split"
    ]

    # =========================
    # STATUS BADGES
    # =========================

    def deposit_state_badge(self, obj):

        color_map = {
            "held": "#3b82f6",
            "returned_full": "#10b981",
            "returned_half": "#f59e0b",
            "forfeited": "#ef4444",
            "dispute": "#dc2626",
        }

        label_map = {
            "held": "Held",
            "returned_full": "Full Returned",
            "returned_half": "50% Deducted",
            "forfeited": "Forfeited",
            "dispute": "Dispute",
        }

        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; border-radius:20px; font-size:11px;">{}</span>',
            color_map.get(obj.deposit_state, "#64748b"),
            label_map.get(obj.deposit_state, obj.deposit_state),
        )

    deposit_state_badge.short_description = "Deposit Status"

    def dispute_badge(self, obj):

        if obj.dispute_open:
            return format_html(
                '<span style="color:{}; font-weight:bold;">● {}</span>',
                "#dc2626",
                "OPEN"
            )

        return format_html(
            '<span style="color:{};">{}</span>',
            "#10b981",
            "Resolved"
        )

    dispute_badge.short_description = "Dispute"

    # =========================
    # ADMIN RESOLUTION ACTIONS
    # =========================

    @admin.action(description="Refund FULL Deposit to Borrower")
    def resolve_full_refund(self, request, queryset):

        for payment in queryset:
            if payment.deposit_state != "dispute":
                continue

            with transaction.atomic():
                borrower_wallet = Wallet.objects.get(user=payment.borrower)
                deposit = Decimal(payment.deposit)

                borrower_wallet.balance += deposit
                borrower_wallet.save()

                payment.deposit_state = "returned_full"
                payment.dispute_open = False
                payment.dispute_resolved = True
                payment.deposit_locked = False
                payment.deposit_status = True
                payment.save()


    @admin.action(description="Give FULL Deposit to Lender")
    def resolve_give_lender(self, request, queryset):

        for payment in queryset:
            if payment.deposit_state != "dispute":
                continue

            with transaction.atomic():
                lender_wallet = Wallet.objects.get(user=payment.lender)
                deposit = Decimal(payment.deposit)

                lender_wallet.balance += deposit
                lender_wallet.save()

                payment.deposit_state = "forfeited"
                payment.dispute_open = False
                payment.dispute_resolved = True
                payment.deposit_locked = False
                payment.deposit_status = True
                payment.save()


    @admin.action(description="Split Deposit 50-50")
    def resolve_split(self, request, queryset):

        for payment in queryset:
            if payment.deposit_state != "dispute":
                continue

            with transaction.atomic():

                borrower_wallet = Wallet.objects.get(user=payment.borrower)
                lender_wallet = Wallet.objects.get(user=payment.lender)

                deposit = Decimal(payment.deposit)
                half = deposit / Decimal("2")

                borrower_wallet.balance += half
                lender_wallet.balance += half

                borrower_wallet.save()
                lender_wallet.save()

                payment.deposit_state = "returned_half"
                payment.dispute_open = False
                payment.dispute_resolved = True
                payment.deposit_locked = False
                payment.deposit_status = True
                payment.save()

# @admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "balance_card",
        "held_deposit",
        "pending_earnings",
    )

    def balance_card(self, obj):
        return format_html(
            '<div style="background:#f0fdfa; padding:5px; '
            'border-radius:5px; text-align:center; '
            'border:1px solid #ccfbf1">₹{}</div>',
            obj.balance
        )

# @admin.register(item_usage)
class ItemUsageAdmin(admin.ModelAdmin):
    
    list_display = (
        "id",
        "item",
        "lender",
        "renter",
        "start_date",
        "end_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
        "created_at",
    )

    search_fields = (
        "item__name",
        "lender__name",
        "lender__email",
        "renter__name",
        "renter__email",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    list_per_page = 20
    
# @admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("item", "reviewer", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("item__name", "reviewer__email")

from django.contrib import admin
from .models import Query

# @admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "get_item_name", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "user__email", "item__name")
    readonly_fields = ("user", "item", "subject", "message", "created_at")
    # Allows admin to resolve it directly from the list
    actions = ['mark_as_resolved']
    def get_item_name(self, obj):
        return obj.item.name if obj.item else "General Query"
    get_item_name.short_description = 'Related Item'
    @admin.action(description='Mark selected reports as Resolved')
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
    
    
# @admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "transaction_type",
        "description",
        "created_at"
    )

    list_filter = ("transaction_type",)
    search_fields = ("user__email",)


# @admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ("image_preview", "name", "created_at")
    search_fields = ("name",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; object-fit:cover; border-radius:6px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Image"



admin_site.register(User, UserAdmin)
admin_site.register(Item, ItemAdmin)
admin_site.register(item_Request, ItemRequestAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(Wallet, WalletAdmin)
admin_site.register(item_usage, ItemUsageAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(Query, QueryAdmin)
admin_site.register(WalletTransaction, WalletTransactionAdmin)
admin_site.register(Category, CategoryAdmin)
