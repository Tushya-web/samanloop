from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum
import csv

from .models import (
    User, Category, Item, ItemImage,
    item_Request, item_usage, payment,
    Review, query, Wallet, WalletTransaction
)

# ==========================
# HELPER FUNCTION
# ==========================

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


# ==========================
# USER ADMIN
# ==========================

@admin.register(User)
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

@admin.register(Item)
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

@admin.register(item_Request)
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


# ==========================
# PAYMENT ADMIN
# ==========================

@admin.register(payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "item_usage",
        "amount_display",
        "deposit_status_badge",
        "payment_date",
    )

    def amount_display(self, obj):
        return format_html(
            '<span style="color:#0d9488; font-weight:bold;">₹{}</span>',
            obj.payment_amt
        )

    def deposit_status_badge(self, obj):
        icon = "check-circle-fill" if obj.deposit_status else "clock"
        color = "#10b981" if obj.deposit_status else "#f59e0b"
        return format_html(
            '<i class="bi bi-{}" style="color:{}"></i>',
            icon, color
        )


# ==========================
# WALLET ADMIN
# ==========================

@admin.register(Wallet)
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

@admin.register(item_usage)
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
    
admin.site.register(Review)
admin.site.register(query)
admin.site.register(WalletTransaction)

@admin.register(Category)
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

