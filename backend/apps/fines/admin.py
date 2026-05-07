from django.contrib import admin
from .models import Fine, OverdueReminder


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['reader', 'borrowing', 'amount', 'overdue_days', 'status', 'paid_date']
    search_fields = ['reader__name', 'reader__reader_id', 'borrowing__book__title']
    list_filter = ['status', 'created_at', 'paid_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OverdueReminder)
class OverdueReminderAdmin(admin.ModelAdmin):
    list_display = ['reader', 'borrowing', 'reminder_type', 'reminder_date', 'is_sent', 'sent_date']
    search_fields = ['reader__name', 'reader__reader_id', 'borrowing__book__title']
    list_filter = ['reminder_type', 'is_sent', 'reminder_date']
    readonly_fields = ['created_at']
