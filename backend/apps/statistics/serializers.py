from rest_framework import serializers
from apps.books.models import Book, Category
from apps.readers.models import Reader
from apps.borrowings.models import Borrowing, Reservation
from apps.fines.models import Fine


class HotBookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    isbn = serializers.CharField()
    author = serializers.CharField()
    borrow_count = serializers.IntegerField()
    category_name = serializers.CharField()


class BorrowTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    borrow_count = serializers.IntegerField()
    return_count = serializers.IntegerField()
    net_count = serializers.IntegerField()


class CategoryStatisticsSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    book_count = serializers.IntegerField()
    borrow_count = serializers.IntegerField()
    available_copies = serializers.IntegerField()


class ReaderStatisticsSerializer(serializers.Serializer):
    total_readers = serializers.IntegerField()
    active_readers = serializers.IntegerField()
    suspended_readers = serializers.IntegerField()
    closed_readers = serializers.IntegerField()
    new_readers_this_month = serializers.IntegerField()


class BookStatisticsSerializer(serializers.Serializer):
    total_books = serializers.IntegerField()
    total_copies = serializers.IntegerField()
    available_copies = serializers.IntegerField()
    borrowed_copies = serializers.IntegerField()
    categories_count = serializers.IntegerField()


class BorrowingStatisticsSerializer(serializers.Serializer):
    total_borrowings = serializers.IntegerField()
    active_borrowings = serializers.IntegerField()
    returned_borrowings = serializers.IntegerField()
    overdue_borrowings = serializers.IntegerField()
    total_reservations = serializers.IntegerField()
    active_reservations = serializers.IntegerField()


class FineStatisticsSerializer(serializers.Serializer):
    total_fines = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    unpaid_fines = serializers.IntegerField()
    unpaid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_fines = serializers.IntegerField()
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    waived_fines = serializers.IntegerField()
    waived_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class DashboardStatisticsSerializer(serializers.Serializer):
    books = BookStatisticsSerializer()
    readers = ReaderStatisticsSerializer()
    borrowings = BorrowingStatisticsSerializer()
    fines = FineStatisticsSerializer()
