from django.contrib import admin
from django.utils.html import format_html

from .models import Book, Category, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "book_count"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}

    @admin.display(description="Kitoblar")
    def book_count(self, obj):
        return obj.books.count()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["swatch", "title", "author", "category", "price", "stock", "is_featured"]
    list_display_links = ["title"]
    list_editable = ["price", "stock", "is_featured"]
    list_filter = ["category", "language", "is_featured"]
    search_fields = ["title", "author"]
    prepopulated_fields = {"slug": ["title"]}

    @admin.display(description="")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:20px;border-radius:2px;'
            'background:{};border-left:3px solid {}"></span>',
            obj.cover_color, obj.accent_color,
        )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["book", "price", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["number", "full_name", "phone", "region", "delivery_method",
                    "payment_method", "total", "is_paid", "status", "created"]
    list_filter = ["status", "is_paid", "delivery_method", "payment_method", "region"]
    list_editable = ["status"]
    search_fields = ["full_name", "phone", "street"]
    readonly_fields = ["code", "subtotal", "delivery_price", "total", "paid_at", "transaction_id"]
    inlines = [OrderItemInline]
    fieldsets = [
        ("Mijoz", {"fields": ["full_name", "phone", "email"]}),
        ("Manzil", {"fields": ["region", "city", "street", "house", "apartment", "landmark", "note"]}),
        ("Yetkazish va to‘lov", {"fields": ["delivery_method", "payment_method", "is_paid",
                                            "paid_at", "transaction_id", "status"]}),
        ("Summalar", {"fields": ["subtotal", "delivery_price", "total", "code"]}),
    ]
