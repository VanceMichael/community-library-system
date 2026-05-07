from django.contrib import admin
from .models import Category, Book


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'author', 'category', 'location', 'total_copies', 'available_copies', 'status', 'created_at']
    search_fields = ['title', 'isbn', 'author', 'publisher']
    list_filter = ['category', 'status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
