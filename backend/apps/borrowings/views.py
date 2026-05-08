from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Borrowing, Reservation
from .serializers import (
    BorrowingSerializer, BorrowingListSerializer, BorrowingCreateSerializer,
    ReservationSerializer, ReservationCreateSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related('reader', 'book').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'reader', 'book']
    search_fields = ['reader__name', 'reader__reader_id', 'book__title', 'book__isbn']
    ordering_fields = ['borrow_date', 'due_date', 'return_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return BorrowingListSerializer
        elif self.action == 'create':
            return BorrowingCreateSerializer
        return BorrowingSerializer

    @action(detail=False, methods=['get'])
    def my_borrowings(self, request):
        reader = getattr(request.user, 'reader', None)
        if not reader:
            return Response({'error': '用户不是读者'}, status=status.HTTP_400_BAD_REQUEST)
        borrowings = Borrowing.objects.filter(reader=reader)
        serializer = BorrowingListSerializer(borrowings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_borrowings = Borrowing.objects.filter(
            status__in=['borrowed', 'overdue'],
            due_date__lt=timezone.now()
        )
        for borrowing in overdue_borrowings:
            if borrowing.status == 'borrowed':
                borrowing.status = 'overdue'
                borrowing.save()
        serializer = BorrowingListSerializer(overdue_borrowings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.status in ['returned', 'lost']:
            return Response({'error': '该图书已归还或丢失'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            borrowing.return_date = timezone.now()
            borrowing.status = 'returned'
            fine = borrowing.calculate_fine()
            borrowing.fine_amount = fine
            borrowing.save()

            if fine > Decimal('0.00'):
                from apps.fines.models import Fine
                Fine.objects.get_or_create(
                    borrowing=borrowing,
                    defaults={
                        'reader': borrowing.reader,
                        'amount': fine,
                        'overdue_days': borrowing.get_overdue_days(),
                        'status': 'unpaid',
                    }
                )

            book = borrowing.book
            book.available_copies += 1
            book.save()

            reader = borrowing.reader
            if reader.borrow_count > 0:
                reader.borrow_count -= 1
                reader.save()

            pending_reservations = Reservation.objects.filter(
                book=book,
                status='pending'
            ).order_by('queue_position')

            if pending_reservations.exists():
                reservation = pending_reservations.first()
                reservation.status = 'available'
                reservation.available_date = timezone.now()
                reservation.expire_date = timezone.now() + timedelta(days=7)
                reservation.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        borrowing = self.get_object()

        can_renew, message = borrowing.can_renew()
        if not can_renew:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            borrowing.renew_count += 1
            borrow_days = 30
            if borrowing.due_date > timezone.now():
                borrowing.due_date = borrowing.due_date + timedelta(days=borrow_days)
            else:
                borrowing.due_date = timezone.now() + timedelta(days=borrow_days)
            borrowing.status = 'borrowed'
            borrowing.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('reader', 'book').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'reader', 'book']
    search_fields = ['reader__name', 'reader__reader_id', 'book__title', 'book__isbn']
    ordering_fields = ['reserve_date', 'queue_position']

    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer

    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        reader = getattr(request.user, 'reader', None)
        if not reader:
            return Response({'error': '用户不是读者'}, status=status.HTTP_400_BAD_REQUEST)
        reservations = Reservation.objects.filter(reader=reader)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status not in ['pending', 'available']:
            return Response({'error': '该预约无法取消'}, status=status.HTTP_400_BAD_REQUEST)

        book = reservation.book

        with transaction.atomic():
            reservation.status = 'cancelled'
            reservation.save()

            later_reservations = Reservation.objects.filter(
                book=book,
                status__in=['pending', 'available'],
                queue_position__gt=reservation.queue_position
            ).order_by('queue_position')

            for res in later_reservations:
                res.queue_position -= 1
                res.save()

        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status != 'available':
            return Response({'error': '该预约状态不可领取'}, status=status.HTTP_400_BAD_REQUEST)

        reader = reservation.reader
        book = reservation.book

        can_borrow, message = reader.can_borrow()
        if not can_borrow:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        if book.available_copies <= 0:
            return Response({'error': '该书库存不足'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            borrowing = Borrowing.objects.create(
                reader=reader,
                book=book
            )

            book.available_copies -= 1
            book.save()

            reader.borrow_count += 1
            reader.save()

            reservation.status = 'completed'
            reservation.save()

            later_reservations = Reservation.objects.filter(
                book=book,
                status='pending'
            ).order_by('queue_position')

            for res in later_reservations:
                res.queue_position -= 1
                res.save()

        return Response({
            'message': '领取成功',
            'borrowing': BorrowingSerializer(borrowing).data
        })
