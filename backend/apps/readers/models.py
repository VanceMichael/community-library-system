from django.db import models
from django.contrib.auth.models import User


class Reader(models.Model):
    STATUS_CHOICES = [
        ('active', '正常'),
        ('suspended', '挂失'),
        ('closed', '注销'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reader', verbose_name='关联用户')
    reader_id = models.CharField(max_length=20, unique=True, verbose_name='读者证号')
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女')], blank=True, null=True, verbose_name='性别')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    email = models.EmailField(blank=True, null=True, verbose_name='电子邮箱')
    address = models.TextField(blank=True, null=True, verbose_name='联系地址')
    id_card = models.CharField(max_length=18, unique=True, verbose_name='身份证号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    borrow_limit = models.PositiveIntegerField(default=5, verbose_name='借阅限额')
    borrow_count = models.PositiveIntegerField(default=0, verbose_name='当前借阅数')
    register_date = models.DateField(auto_now_add=True, verbose_name='注册日期')
    expire_date = models.DateField(blank=True, null=True, verbose_name='有效期至')
    photo = models.ImageField(upload_to='reader_photos/', blank=True, null=True, verbose_name='照片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '读者'
        verbose_name_plural = '读者'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.reader_id})"

    def can_borrow(self):
        if self.status != 'active':
            return False, '读者证状态异常'
        if self.borrow_count >= self.borrow_limit:
            return False, f'已达到借阅限额 ({self.borrow_limit}本)'
        return True, '可以借阅'
