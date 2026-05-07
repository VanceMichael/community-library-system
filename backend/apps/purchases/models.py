from django.db import models
from apps.readers.models import Reader
from django.contrib.auth.models import User


class PurchaseSuggestion(models.Model):
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('purchased', '已采购'),
        ('cancelled', '已取消'),
    ]

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='purchase_suggestions', verbose_name='推荐读者')
    isbn = models.CharField(max_length=13, verbose_name='ISBN')
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    publisher = models.CharField(max_length=100, blank=True, null=True, verbose_name='出版社')
    publish_date = models.DateField(blank=True, null=True, verbose_name='出版日期')
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name='分类')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='预估价格')
    reason = models.TextField(verbose_name='推荐理由')
    quantity = models.PositiveIntegerField(default=1, verbose_name='推荐采购数量')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_suggestions', verbose_name='审核人')
    review_date = models.DateTimeField(blank=True, null=True, verbose_name='审核日期')
    review_comment = models.TextField(blank=True, null=True, verbose_name='审核意见')
    purchase_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name='实际采购数量')
    purchase_date = models.DateField(blank=True, null=True, verbose_name='采购日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '采购建议'
        verbose_name_plural = '采购建议'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.reader.name}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已批准'),
        ('ordered', '已订购'),
        ('received', '已到货'),
        ('cancelled', '已取消'),
    ]

    order_number = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    supplier = models.CharField(max_length=200, verbose_name='供应商')
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系电话')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_purchase_orders', verbose_name='创建人')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchase_orders', verbose_name='批准人')
    approval_date = models.DateTimeField(blank=True, null=True, verbose_name='批准日期')
    order_date = models.DateField(blank=True, null=True, verbose_name='订购日期')
    receive_date = models.DateField(blank=True, null=True, verbose_name='到货日期')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '采购订单'
        verbose_name_plural = '采购订单'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='采购订单')
    purchase_suggestion = models.ForeignKey(PurchaseSuggestion, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items', verbose_name='关联采购建议')
    isbn = models.CharField(max_length=13, verbose_name='ISBN')
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    publisher = models.CharField(max_length=100, blank=True, null=True, verbose_name='出版社')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='小计')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '采购订单项'
        verbose_name_plural = '采购订单项'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} x {self.quantity}"
