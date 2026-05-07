from rest_framework import serializers
from .models import Category, Book


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'description', 'book_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_book_count(self, obj):
        return obj.books.count()


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'publisher', 'publish_date',
            'category', 'category_name', 'category_code', 'location',
            'total_copies', 'available_copies', 'status', 'description',
            'cover_image', 'price', 'pages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'category_name', 'location',
            'available_copies', 'status', 'cover_image'
        ]
