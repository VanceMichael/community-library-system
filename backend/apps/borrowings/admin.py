from django.contrib import admin
from .models import Borrowing, Reservation


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ['reader', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'fine_amount']
    search_fields = ['reader__name', 'reader__reader_id', 'book__title', 'book__isbn']
    list_filter = ['status', 'borrow_date', 'due_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['reader', 'book', 'reserve_date', 'status', 'queue_position']
    search_fields = ['reader__name', 'reader__reader_id', 'book__title', 'book__isbn']
    list_filter = ['status', 'reserve_date']
    readonly_fields = ['created_at', 'updated_at']
