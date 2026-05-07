from rest_framework import serializers
from .models import Borrowing, Reservation


class BorrowingSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    reader_id = serializers.CharField(source='reader.reader_id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    overdue_days = serializers.SerializerMethodField()
    current_fine = serializers.SerializerMethodField()
    can_renew = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            'id', 'reader', 'reader_name', 'reader_id',
            'book', 'book_title', 'book_isbn',
            'borrow_date', 'due_date', 'return_date',
            'renew_count', 'max_renew_count', 'status',
            'fine_amount', 'fine_paid', 'overdue_days',
            'current_fine', 'can_renew', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'borrow_date', 'due_date', 'return_date', 'renew_count',
            'max_renew_count', 'status', 'fine_amount', 'fine_paid',
            'created_at', 'updated_at'
        ]

    def get_overdue_days(self, obj):
        return obj.get_overdue_days()

    def get_current_fine(self, obj):
        return obj.calculate_fine()

    def get_can_renew(self, obj):
        can_renew, message = obj.can_renew()
        return {'can_renew': can_renew, 'message': message}


class BorrowingListSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    overdue_days = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            'id', 'reader_name', 'book_title', 'borrow_date',
            'due_date', 'status', 'renew_count', 'overdue_days'
        ]

    def get_overdue_days(self, obj):
        return obj.get_overdue_days()


class BorrowingCreateSerializer(serializers.Serializer):
    reader_id = serializers.IntegerField(write_only=True)
    book_id = serializers.IntegerField(write_only=True)

    def validate(self, data):
        from apps.readers.models import Reader
        from apps.books.models import Book

        reader = Reader.objects.filter(id=data['reader_id']).first()
        if not reader:
            raise serializers.ValidationError('读者不存在')

        can_borrow, message = reader.can_borrow()
        if not can_borrow:
            raise serializers.ValidationError(message)

        book = Book.objects.filter(id=data['book_id']).first()
        if not book:
            raise serializers.ValidationError('图书不存在')

        if book.available_copies <= 0:
            raise serializers.ValidationError('该书库存不足')

        if Borrowing.objects.filter(reader=reader, book=book, status__in=['borrowed', 'overdue']).exists():
            raise serializers.ValidationError('该读者已借阅过此书，尚未归还')

        return data

    def create(self, validated_data):
        from apps.readers.models import Reader
        from apps.books.models import Book
        from django.db import transaction

        reader = Reader.objects.get(id=validated_data['reader_id'])
        book = Book.objects.get(id=validated_data['book_id'])

        with transaction.atomic():
            borrowing = Borrowing.objects.create(reader=reader, book=book)
            book.available_copies -= 1
            book.save()
            reader.borrow_count += 1
            reader.save()

        return borrowing


class ReservationSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'reader', 'reader_name', 'book', 'book_title',
            'reserve_date', 'available_date', 'expire_date',
            'status', 'queue_position', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'reserve_date', 'available_date', 'expire_date',
            'status', 'queue_position', 'created_at', 'updated_at'
        ]


class ReservationCreateSerializer(serializers.Serializer):
    reader_id = serializers.IntegerField(write_only=True)
    book_id = serializers.IntegerField(write_only=True)

    def validate(self, data):
        from apps.readers.models import Reader
        from apps.books.models import Book

        reader = Reader.objects.filter(id=data['reader_id']).first()
        if not reader:
            raise serializers.ValidationError('读者不存在')

        if reader.status != 'active':
            raise serializers.ValidationError('读者证状态异常，无法预约')

        book = Book.objects.filter(id=data['book_id']).first()
        if not book:
            raise serializers.ValidationError('图书不存在')

        if Reservation.objects.filter(reader=reader, book=book, status__in=['pending', 'available']).exists():
            raise serializers.ValidationError('您已预约过此书')

        if Borrowing.objects.filter(reader=reader, book=book, status__in=['borrowed', 'overdue']).exists():
            raise serializers.ValidationError('您已借阅过此书，无需预约')

        return data

    def create(self, validated_data):
        from apps.readers.models import Reader
        from apps.books.models import Book
        from django.utils import timezone
        from datetime import timedelta

        reader = Reader.objects.get(id=validated_data['reader_id'])
        book = Book.objects.get(id=validated_data['book_id'])

        queue_position = Reservation.objects.filter(book=book, status__in=['pending', 'available']).count() + 1

        reservation = Reservation.objects.create(
            reader=reader,
            book=book,
            queue_position=queue_position,
            status='pending'
        )

        if book.available_copies > 0:
            reservation.status = 'available'
            reservation.available_date = timezone.now()
            reservation.expire_date = timezone.now() + timedelta(days=7)
            reservation.save()

        return reservation
