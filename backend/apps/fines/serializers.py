from rest_framework import serializers
from .models import Fine, OverdueReminder


class FineSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    reader_id = serializers.CharField(source='reader.reader_id', read_only=True)
    book_title = serializers.CharField(source='borrowing.book.title', read_only=True)
    book_isbn = serializers.CharField(source='borrowing.book.isbn', read_only=True)
    borrow_date = serializers.DateTimeField(source='borrowing.borrow_date', read_only=True)
    due_date = serializers.DateTimeField(source='borrowing.due_date', read_only=True)

    class Meta:
        model = Fine
        fields = [
            'id', 'borrowing', 'reader', 'reader_name', 'reader_id',
            'book_title', 'book_isbn', 'borrow_date', 'due_date',
            'amount', 'overdue_days', 'status', 'paid_date',
            'paid_by', 'remark', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FineListSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    book_title = serializers.CharField(source='borrowing.book.title', read_only=True)

    class Meta:
        model = Fine
        fields = [
            'id', 'reader_name', 'book_title', 'amount',
            'overdue_days', 'status', 'created_at'
        ]


class OverdueReminderSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    book_title = serializers.CharField(source='borrowing.book.title', read_only=True)

    class Meta:
        model = OverdueReminder
        fields = [
            'id', 'borrowing', 'reader', 'reader_name', 'book_title',
            'reminder_type', 'reminder_date', 'message', 'is_sent',
            'sent_date', 'remark', 'created_at'
        ]
        read_only_fields = ['reminder_date', 'created_at']
