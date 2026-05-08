from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
from .models import Fine, OverdueReminder
from apps.borrowings.models import Borrowing
from .serializers import FineSerializer, FineListSerializer, OverdueReminderSerializer


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.select_related('reader', 'borrowing', 'borrowing__book').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'reader']
    search_fields = ['reader__name', 'reader__reader_id', 'borrowing__book__title']
    ordering_fields = ['amount', 'overdue_days', 'created_at', 'paid_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return FineListSerializer
        return FineSerializer

    @action(detail=False, methods=['post'])
    def generate_fines(self, request):
        overdue_borrowings = Borrowing.objects.filter(
            fine__isnull=True
        ).filter(
            models.Q(status__in=['borrowed', 'overdue'], due_date__lt=timezone.now()) |
            models.Q(status='returned', fine_amount__gt=0)
        )

        created_fines = []
        for borrowing in overdue_borrowings:
            if borrowing.status == 'borrowed':
                borrowing.status = 'overdue'
                borrowing.save()

            overdue_days = borrowing.get_overdue_days()
            fine_amount = borrowing.calculate_fine()

            if fine_amount <= 0:
                continue

            fine, created = Fine.objects.get_or_create(
                borrowing=borrowing,
                defaults={
                    'reader': borrowing.reader,
                    'amount': fine_amount,
                    'overdue_days': overdue_days,
                    'status': 'unpaid'
                }
            )

            if created:
                created_fines.append(fine)

        return Response({
            'message': f'已生成 {len(created_fines)} 条罚款记录',
            'fines': FineListSerializer(created_fines, many=True).data
        })

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        fine = self.get_object()

        if fine.status == 'paid':
            return Response({'error': '罚款已缴纳'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            fine.status = 'paid'
            fine.paid_date = timezone.now()
            fine.paid_by = request.user.username if request.user.is_authenticated else '系统'
            fine.save()

            borrowing = fine.borrowing
            borrowing.fine_paid = True
            borrowing.save()

        serializer = FineSerializer(fine)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def waive(self, request, pk=None):
        fine = self.get_object()

        if fine.status != 'unpaid':
            return Response({'error': '只能减免未缴纳的罚款'}, status=status.HTTP_400_BAD_REQUEST)

        remark = request.data.get('remark', '')

        with transaction.atomic():
            fine.status = 'waived'
            fine.remark = remark
            fine.paid_by = request.user.username if request.user.is_authenticated else '系统'
            fine.save()

        serializer = FineSerializer(fine)
        return Response(serializer.data)


class OverdueReminderViewSet(viewsets.ModelViewSet):
    queryset = OverdueReminder.objects.select_related('reader', 'borrowing', 'borrowing__book').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['reminder_type', 'is_sent', 'reader']
    search_fields = ['reader__name', 'reader__reader_id', 'borrowing__book__title']
    ordering_fields = ['reminder_date', 'sent_date']

    def get_serializer_class(self):
        return OverdueReminderSerializer

    @action(detail=False, methods=['post'])
    def generate_reminders(self, request):
        reminder_type = request.data.get('reminder_type', 'email')
        days_before_due = request.data.get('days_before_due', 3)

        now = timezone.now()
        upcoming_due = Borrowing.objects.filter(
            status='borrowed',
            due_date__lte=now + timedelta(days=days_before_due),
            due_date__gt=now
        )

        created_reminders = []
        for borrowing in upcoming_due:
            days_left = (borrowing.due_date - now).days
            message = f"尊敬的读者 {borrowing.reader.name}，您借阅的图书《{borrowing.book.title}》将于 {days_left} 天后到期（应还日期：{borrowing.due_date.strftime('%Y-%m-%d')}）。请按时归还或办理续借手续。"

            reminder = OverdueReminder.objects.create(
                borrowing=borrowing,
                reader=borrowing.reader,
                reminder_type=reminder_type,
                message=message,
                is_sent=False
            )
            created_reminders.append(reminder)

        overdue_borrowings = Borrowing.objects.filter(
            status__in=['borrowed', 'overdue'],
            due_date__lt=now
        )

        for borrowing in overdue_borrowings:
            overdue_days = borrowing.get_overdue_days()
            fine = borrowing.calculate_fine()
            message = f"尊敬的读者 {borrowing.reader.name}，您借阅的图书《{borrowing.book.title}》已逾期 {overdue_days} 天（应还日期：{borrowing.due_date.strftime('%Y-%m-%d')}）。当前产生罚款 ¥{fine:.2f}。请尽快归还图书并缴纳罚款。"

            reminder = OverdueReminder.objects.create(
                borrowing=borrowing,
                reader=borrowing.reader,
                reminder_type=reminder_type,
                message=message,
                is_sent=False
            )
            created_reminders.append(reminder)

        return Response({
            'message': f'已生成 {len(created_reminders)} 条提醒记录',
            'reminders': OverdueReminderSerializer(created_reminders, many=True).data
        })

    @action(detail=True, methods=['post'])
    def mark_as_sent(self, request, pk=None):
        reminder = self.get_object()

        if reminder.is_sent:
            return Response({'error': '该提醒已标记为已发送'}, status=status.HTTP_400_BAD_REQUEST)

        reminder.is_sent = True
        reminder.sent_date = timezone.now()
        reminder.save()

        serializer = OverdueReminderSerializer(reminder)
        return Response(serializer.data)
