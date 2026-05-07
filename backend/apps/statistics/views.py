from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.books.models import Book, Category
from apps.readers.models import Reader
from apps.borrowings.models import Borrowing, Reservation
from apps.fines.models import Fine
from .serializers import (
    HotBookSerializer, BorrowTrendSerializer, CategoryStatisticsSerializer,
    ReaderStatisticsSerializer, BookStatisticsSerializer,
    BorrowingStatisticsSerializer, FineStatisticsSerializer,
    DashboardStatisticsSerializer
)


class StatisticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        total_books = Book.objects.count()
        total_copies = Book.objects.aggregate(Sum('total_copies'))['total_copies__sum'] or 0
        available_copies = Book.objects.aggregate(Sum('available_copies'))['available_copies__sum'] or 0
        borrowed_copies = total_copies - available_copies
        categories_count = Category.objects.count()

        book_stats = {
            'total_books': total_books,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'borrowed_copies': borrowed_copies,
            'categories_count': categories_count
        }

        total_readers = Reader.objects.count()
        active_readers = Reader.objects.filter(status='active').count()
        suspended_readers = Reader.objects.filter(status='suspended').count()
        closed_readers = Reader.objects.filter(status='closed').count()

        first_day_of_month = timezone.now().replace(day=1)
        new_readers_this_month = Reader.objects.filter(register_date__gte=first_day_of_month.date()).count()

        reader_stats = {
            'total_readers': total_readers,
            'active_readers': active_readers,
            'suspended_readers': suspended_readers,
            'closed_readers': closed_readers,
            'new_readers_this_month': new_readers_this_month
        }

        total_borrowings = Borrowing.objects.count()
        active_borrowings = Borrowing.objects.filter(status__in=['borrowed', 'overdue']).count()
        returned_borrowings = Borrowing.objects.filter(status='returned').count()
        overdue_borrowings = Borrowing.objects.filter(status='overdue').count()
        total_reservations = Reservation.objects.count()
        active_reservations = Reservation.objects.filter(status__in=['pending', 'available']).count()

        borrowing_stats = {
            'total_borrowings': total_borrowings,
            'active_borrowings': active_borrowings,
            'returned_borrowings': returned_borrowings,
            'overdue_borrowings': overdue_borrowings,
            'total_reservations': total_reservations,
            'active_reservations': active_reservations
        }

        total_fines = Fine.objects.count()
        total_amount = Fine.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        unpaid_fines = Fine.objects.filter(status='unpaid').count()
        unpaid_amount = Fine.objects.filter(status='unpaid').aggregate(Sum('amount'))['amount__sum'] or 0
        paid_fines = Fine.objects.filter(status='paid').count()
        paid_amount = Fine.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        waived_fines = Fine.objects.filter(status='waived').count()
        waived_amount = Fine.objects.filter(status='waived').aggregate(Sum('amount'))['amount__sum'] or 0

        fine_stats = {
            'total_fines': total_fines,
            'total_amount': total_amount,
            'unpaid_fines': unpaid_fines,
            'unpaid_amount': unpaid_amount,
            'paid_fines': paid_fines,
            'paid_amount': paid_amount,
            'waived_fines': waived_fines,
            'waived_amount': waived_amount
        }

        data = {
            'books': book_stats,
            'readers': reader_stats,
            'borrowings': borrowing_stats,
            'fines': fine_stats
        }

        serializer = DashboardStatisticsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hot_books(self, request):
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 10

        hot_books = Book.objects.annotate(
            borrow_count=Count('borrowings')
        ).filter(
            borrow_count__gt=0
        ).order_by('-borrow_count')[:limit]

        result = []
        for book in hot_books:
            result.append({
                'id': book.id,
                'title': book.title,
                'isbn': book.isbn,
                'author': book.author,
                'borrow_count': book.borrow_count,
                'category_name': book.category.name if book.category else '未分类'
            })

        serializer = HotBookSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def borrow_trend(self, request):
        days = request.query_params.get('days', 30)
        try:
            days = int(days)
        except (ValueError, TypeError):
            days = 30

        now = timezone.now()
        start_date = now - timedelta(days=days)

        borrowings = Borrowing.objects.filter(
            borrow_date__gte=start_date
        ).annotate(
            date=TruncDate('borrow_date')
        ).values('date').annotate(
            borrow_count=Count('id')
        ).order_by('date')

        returns = Borrowing.objects.filter(
            return_date__gte=start_date
        ).annotate(
            date=TruncDate('return_date')
        ).values('date').annotate(
            return_count=Count('id')
        ).order_by('date')

        borrow_dict = {}
        for item in borrowings:
            date_val = item['date']
            if hasattr(date_val, 'date'):
                date_val = date_val.date()
            borrow_dict[date_val] = item['borrow_count']

        return_dict = {}
        for item in returns:
            date_val = item['date']
            if hasattr(date_val, 'date'):
                date_val = date_val.date()
            return_dict[date_val] = item['return_count']

        result = []
        for i in range(days + 1):
            date = (start_date + timedelta(days=i)).date()
            borrow_count = borrow_dict.get(date, 0)
            return_count = return_dict.get(date, 0)
            result.append({
                'date': date,
                'borrow_count': borrow_count,
                'return_count': return_count,
                'net_count': borrow_count - return_count
            })

        serializer = BorrowTrendSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def category_statistics(self, request):
        categories = Category.objects.annotate(
            book_count=Count('books')
        ).prefetch_related('books')

        result = []
        for category in categories:
            borrow_count = Borrowing.objects.filter(
                book__category=category
            ).count()

            available_copies = category.books.aggregate(
                Sum('available_copies')
            )['available_copies__sum'] or 0

            result.append({
                'category_id': category.id,
                'category_name': category.name,
                'book_count': category.book_count,
                'borrow_count': borrow_count,
                'available_copies': available_copies
            })

        serializer = CategoryStatisticsSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly_statistics(self, request):
        months = request.query_params.get('months', 12)
        try:
            months = int(months)
        except (ValueError, TypeError):
            months = 12

        start_date = timezone.now() - timedelta(days=months * 30)

        borrowings = Borrowing.objects.filter(
            borrow_date__gte=start_date
        ).annotate(
            month=TruncMonth('borrow_date')
        ).values('month').annotate(
            borrow_count=Count('id')
        ).order_by('month')

        returns = Borrowing.objects.filter(
            return_date__gte=start_date
        ).annotate(
            month=TruncMonth('return_date')
        ).values('month').annotate(
            return_count=Count('id')
        ).order_by('month')

        fines = Fine.objects.filter(
            created_at__gte=start_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            fine_count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('month')

        borrow_dict = {item['month']: item['borrow_count'] for item in borrowings}
        return_dict = {item['month']: item['return_count'] for item in returns}
        fine_dict = {item['month']: {'count': item['fine_count'], 'amount': item['total_amount']} for item in fines}

        result = []
        for i in range(months):
            month_date = (start_date + timedelta(days=i * 30)).replace(day=1)
            month = month_date.date()
            borrow_count = borrow_dict.get(month, 0)
            return_count = return_dict.get(month, 0)
            fine_data = fine_dict.get(month, {'count': 0, 'amount': 0})

            result.append({
                'month': month,
                'borrow_count': borrow_count,
                'return_count': return_count,
                'fine_count': fine_data['count'],
                'fine_amount': fine_data['amount']
            })

        return Response(result)

    @action(detail=False, methods=['get'])
    def reader_activity(self, request):
        active_readers = Reader.objects.filter(
            borrowings__status__in=['borrowed', 'overdue']
        ).distinct().count()

        top_readers = Reader.objects.annotate(
            borrow_count=Count('borrowings')
        ).filter(
            borrow_count__gt=0
        ).order_by('-borrow_count')[:10]

        result = {
            'active_readers': active_readers,
            'top_readers': [
                {
                    'id': reader.id,
                    'name': reader.name,
                    'reader_id': reader.reader_id,
                    'borrow_count': reader.borrow_count
                }
                for reader in top_readers
            ]
        }

        return Response(result)
