from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='分类代码')
    description = models.TextField(blank=True, null=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = '图书分类'
        ordering = ['code']

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', '可借'),
        ('borrowed', '已借出'),
        ('reserved', '已预约'),
        ('maintenance', '维护中'),
        ('lost', '已丢失'),
    ]

    isbn = models.CharField(max_length=13, unique=True, verbose_name='ISBN')
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    publisher = models.CharField(max_length=100, blank=True, null=True, verbose_name='出版社')
    publish_date = models.DateField(blank=True, null=True, verbose_name='出版日期')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name='分类')
    location = models.CharField(max_length=100, verbose_name='馆藏位置')
    total_copies = models.PositiveIntegerField(default=1, verbose_name='总馆藏数')
    available_copies = models.PositiveIntegerField(default=1, verbose_name='可借数量')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='状态')
    description = models.TextField(blank=True, null=True, verbose_name='图书描述')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name='封面图片')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='价格')
    pages = models.PositiveIntegerField(blank=True, null=True, verbose_name='页数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        if self.available_copies > 0:
            self.status = 'available'
        else:
            self.status = 'borrowed'
        super().save(*args, **kwargs)
