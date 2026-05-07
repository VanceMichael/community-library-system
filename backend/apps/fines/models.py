from django.db import models
from apps.readers.models import Reader
from apps.borrowings.models import Borrowing


class Fine(models.Model):
    STATUS_CHOICES = [
        ('unpaid', '未缴纳'),
        ('paid', '已缴纳'),
        ('waived', '已减免'),
    ]

    borrowing = models.OneToOneField(Borrowing, on_delete=models.CASCADE, related_name='fine', verbose_name='借阅记录')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='fines', verbose_name='读者')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='罚款金额')
    overdue_days = models.PositiveIntegerField(verbose_name='逾期天数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
    paid_date = models.DateTimeField(blank=True, null=True, verbose_name='缴纳日期')
    paid_by = models.CharField(max_length=100, blank=True, null=True, verbose_name='经办人')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '罚款记录'
        verbose_name_plural = '罚款记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reader.name} - ¥{self.amount}"


class OverdueReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('email', '邮件'),
        ('sms', '短信'),
        ('phone', '电话'),
        ('letter', '信函'),
    ]

    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='reminders', verbose_name='借阅记录')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='reminders', verbose_name='读者')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name='提醒方式')
    reminder_date = models.DateTimeField(auto_now_add=True, verbose_name='提醒日期')
    message = models.TextField(verbose_name='提醒内容')
    is_sent = models.BooleanField(default=False, verbose_name='是否已发送')
    sent_date = models.DateTimeField(blank=True, null=True, verbose_name='发送日期')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '逾期提醒'
        verbose_name_plural = '逾期提醒'
        ordering = ['-reminder_date']

    def __str__(self):
        return f"{self.reader.name} - {self.get_reminder_type_display()}"
