from django.contrib import admin
from .models import Reader


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['reader_id', 'name', 'phone', 'status', 'borrow_limit', 'borrow_count', 'register_date']
    search_fields = ['reader_id', 'name', 'phone', 'id_card']
    list_filter = ['status', 'gender', 'register_date']
    readonly_fields = ['created_at', 'updated_at']
