from django.contrib import admin
from .models import PurchaseSuggestion, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseSuggestion)
class PurchaseSuggestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'author', 'reader', 'status', 'quantity', 'created_at']
    search_fields = ['title', 'isbn', 'author', 'reader__name']
    list_filter = ['status', 'category', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'total_amount', 'status', 'created_by', 'created_at']
    search_fields = ['order_number', 'supplier', 'contact_person']
    list_filter = ['status', 'created_at', 'order_date']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'title', 'isbn', 'quantity', 'unit_price', 'subtotal']
    search_fields = ['title', 'isbn', 'purchase_order__order_number']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
