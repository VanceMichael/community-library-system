from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.books.models import Book
from apps.readers.models import Reader
from datetime import timedelta


def make_aware_if_naive(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


class Borrowing(models.Model):
    STATUS_CHOICES = [
        ('borrowed', '借阅中'),
        ('returned', '已归还'),
        ('overdue', '已逾期'),
        ('lost', '已丢失'),
    ]

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='borrowings', verbose_name='读者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings', verbose_name='图书')
    borrow_date = models.DateTimeField(auto_now_add=True, verbose_name='借书日期')
    due_date = models.DateTimeField(verbose_name='应还日期')
    return_date = models.DateTimeField(blank=True, null=True, verbose_name='实际还书日期')
    renew_count = models.PositiveIntegerField(default=0, verbose_name='续借次数')
    max_renew_count = models.PositiveIntegerField(default=2, verbose_name='最大续借次数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed', verbose_name='状态')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='罚款金额')
    fine_paid = models.BooleanField(default=False, verbose_name='罚款已缴纳')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.reader.name} - {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            borrow_days = getattr(settings, 'BORROW_DAYS', 30)
            self.due_date = timezone.now() + timedelta(days=borrow_days)
        super().save(*args, **kwargs)

    def is_overdue(self):
        if self.status == 'lost':
            return False
        due_date = make_aware_if_naive(self.due_date)
        if self.return_date:
            return_date = make_aware_if_naive(self.return_date)
            return return_date > due_date
        now = timezone.now()
        return now > due_date

    def get_overdue_days(self):
        if self.status == 'lost':
            return 0
        due_date = make_aware_if_naive(self.due_date)
        if self.return_date:
            return_date = make_aware_if_naive(self.return_date)
            days = (return_date - due_date).days
            return max(days, 0)
        now = timezone.now()
        days = (now - due_date).days
        return max(days, 0)

    def calculate_fine(self):
        if not self.is_overdue():
            return Decimal('0.00')
        overdue_days = self.get_overdue_days()
        fine_per_day = Decimal(str(getattr(settings, 'OVERDUE_FINE_PER_DAY', 0.1)))
        return Decimal(str(overdue_days)) * fine_per_day

    def can_renew(self):
        if self.status != 'borrowed':
            return False, '该图书已归还或状态异常'
        if self.renew_count >= self.max_renew_count:
            return False, f'已达到最大续借次数 ({self.max_renew_count}次)'
        if self.is_overdue():
            return False, '图书已逾期，无法续借'
        return True, '可以续借'


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('available', '可领取'),
        ('completed', '已领取'),
        ('cancelled', '已取消'),
        ('expired', '已过期'),
    ]

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='reservations', verbose_name='读者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations', verbose_name='图书')
    reserve_date = models.DateTimeField(auto_now_add=True, verbose_name='预约日期')
    available_date = models.DateTimeField(blank=True, null=True, verbose_name='可领取日期')
    expire_date = models.DateTimeField(blank=True, null=True, verbose_name='预约过期日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    queue_position = models.PositiveIntegerField(default=1, verbose_name='预约队列位置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '预约记录'
        verbose_name_plural = '预约记录'
        ordering = ['-reserve_date']

    def __str__(self):
        return f"{self.reader.name} - {self.book.title}"
