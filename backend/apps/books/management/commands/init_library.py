from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from apps.books.models import Category, Book
from apps.readers.models import Reader
from apps.borrowings.models import Borrowing
import random
import string
from datetime import timedelta


class Command(BaseCommand):
    help = 'Initialize the library system with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing library system...')

        admin_username = 'admin'
        admin_password = 'admin123'
        admin_email = 'admin@library.com'

        admin, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': admin_email,
                'is_staff': True,
                'is_superuser': True
            }
        )

        if created:
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {admin_username} / {admin_password}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {admin_username}'))

        categories_data = [
            {'name': '文学小说', 'code': 'LIT', 'description': '文学、小说、散文等作品'},
            {'name': '科技编程', 'code': 'TECH', 'description': '计算机科学、编程技术等'},
            {'name': '历史传记', 'code': 'HIS', 'description': '历史著作、人物传记'},
            {'name': '经济管理', 'code': 'ECO', 'description': '经济学、管理学书籍'},
            {'name': '艺术设计', 'code': 'ART', 'description': '艺术、设计、绘画等'},
            {'name': '教育学习', 'code': 'EDU', 'description': '教育、学习、考试类书籍'},
            {'name': '自然科学', 'code': 'SCI', 'description': '物理、化学、生物等自然科学'},
            {'name': '社会科学', 'code': 'SOC', 'description': '社会学、心理学、政治学等'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category created: {category.name}'))

        books_data = [
            {
                'isbn': '9787111213826',
                'title': 'Python编程：从入门到实践',
                'author': 'Eric Matthes',
                'publisher': '机械工业出版社',
                'category_code': 'TECH',
                'location': 'A-01-01',
                'total_copies': 5,
                'price': 89.00,
                'description': '本书是一本针对所有层次的Python读者而作的Python入门书。'
            },
            {
                'isbn': '9787521707579',
                'title': '深入理解计算机系统',
                'author': 'Randal E.Bryant',
                'publisher': '机械工业出版社',
                'category_code': 'TECH',
                'location': 'A-01-02',
                'total_copies': 3,
                'price': 139.00,
                'description': '本书从程序员的视角详细阐述计算机系统的本质概念。'
            },
            {
                'isbn': '9787544270878',
                'title': '百年孤独',
                'author': '加西亚·马尔克斯',
                'publisher': '南海出版公司',
                'category_code': 'LIT',
                'location': 'B-01-01',
                'total_copies': 8,
                'price': 55.00,
                'description': '《百年孤独》是魔幻现实主义文学的代表作。'
            },
            {
                'isbn': '9787544291170',
                'title': '活着',
                'author': '余华',
                'publisher': '作家出版社',
                'category_code': 'LIT',
                'location': 'B-01-02',
                'total_copies': 6,
                'price': 39.00,
                'description': '《活着》讲述了人如何去承受巨大的苦难。'
            },
            {
                'isbn': '9787100013901',
                'title': '万历十五年',
                'author': '黄仁宇',
                'publisher': '中华书局',
                'category_code': 'HIS',
                'location': 'C-01-01',
                'total_copies': 4,
                'price': 59.00,
                'description': '本书以1587年为切入点，描绘了明朝晚期的社会状况。'
            },
            {
                'isbn': '9787508628924',
                'title': '史蒂夫·乔布斯传',
                'author': '沃尔特·艾萨克森',
                'publisher': '中信出版社',
                'category_code': 'HIS',
                'location': 'C-01-02',
                'total_copies': 5,
                'price': 88.00,
                'description': '这本传记是乔布斯唯一授权的官方传记。'
            },
            {
                'isbn': '9787111407010',
                'title': '算法导论',
                'author': 'Thomas H. Cormen',
                'publisher': '机械工业出版社',
                'category_code': 'TECH',
                'location': 'A-01-03',
                'total_copies': 4,
                'price': 128.00,
                'description': '本书全面、系统地介绍了计算机算法的基本概念、设计方法和分析技术。'
            },
            {
                'isbn': '9787302231776',
                'title': '设计模式：可复用面向对象软件的基础',
                'author': 'Erich Gamma',
                'publisher': '机械工业出版社',
                'category_code': 'TECH',
                'location': 'A-01-04',
                'total_copies': 3,
                'price': 69.00,
                'description': '本书是设计模式领域的经典著作。'
            },
            {
                'isbn': '9787544265449',
                'title': '解忧杂货店',
                'author': '东野圭吾',
                'publisher': '南海出版公司',
                'category_code': 'LIT',
                'location': 'B-01-03',
                'total_copies': 7,
                'price': 39.50,
                'description': '这是一个关于命运与选择的故事。'
            },
            {
                'isbn': '9787508643465',
                'title': '从0到1',
                'author': '彼得·蒂尔',
                'publisher': '中信出版社',
                'category_code': 'ECO',
                'location': 'D-01-01',
                'total_copies': 4,
                'price': 42.00,
                'description': '这本书详细阐述了如何创建新企业。'
            },
        ]

        for book_data in books_data:
            category_code = book_data.pop('category_code')
            category = Category.objects.filter(code=category_code).first()

            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults={
                    **book_data,
                    'category': category,
                    'available_copies': book_data['total_copies']
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Book created: {book.title}'))

        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'testuser@library.com',
                'is_staff': False,
                'is_superuser': False
            }
        )

        if created:
            test_user.set_password('test123')
            test_user.save()

            reader, reader_created = Reader.objects.get_or_create(
                user=test_user,
                defaults={
                    'reader_id': 'R202401010001',
                    'name': '测试读者',
                    'gender': 'male',
                    'phone': '13800138000',
                    'email': 'testuser@library.com',
                    'address': '北京市朝阳区测试街道123号',
                    'id_card': '110101199001011234',
                    'status': 'active',
                    'borrow_limit': 5
                }
            )

            if reader_created:
                self.stdout.write(self.style.SUCCESS(f'Test reader created: testuser / test123'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))
            reader = Reader.objects.filter(user=test_user).first()

        if reader:
            all_books = list(Book.objects.all())
            if all_books:
                now = timezone.now()
                borrow_count = 0

                for i in range(15):
                    book = random.choice(all_books)
                    days_ago = random.randint(1, 29)
                    borrow_date = now - timedelta(days=days_ago)

                    is_returned = random.random() > 0.3
                    if is_returned:
                        return_days = random.randint(1, days_ago)
                        return_date = now - timedelta(days=days_ago - return_days)
                        status = 'returned'
                    else:
                        return_date = None
                        status = 'borrowed'

                    borrowing = Borrowing.objects.create(
                        reader=reader,
                        book=book,
                        status=status,
                        borrow_date=borrow_date,
                        due_date=borrow_date + timedelta(days=30)
                    )
                    if return_date:
                        borrowing.return_date = return_date
                        borrowing.save()

                    borrow_count += 1

                self.stdout.write(self.style.SUCCESS(f'Created {borrow_count} sample borrowing records'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Initialization complete!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('\nAdmin credentials:'))
        self.stdout.write(self.style.SUCCESS(f'  Username: {admin_username}'))
        self.stdout.write(self.style.SUCCESS(f'  Password: {admin_password}'))
        self.stdout.write(self.style.SUCCESS('\nTest reader credentials:'))
        self.stdout.write(self.style.SUCCESS('  Username: testuser'))
        self.stdout.write(self.style.SUCCESS('  Password: test123'))
        self.stdout.write(self.style.SUCCESS('\nSample data created:'))
        self.stdout.write(self.style.SUCCESS(f'  - {Category.objects.count()} categories'))
        self.stdout.write(self.style.SUCCESS(f'  - {Book.objects.count()} books'))
