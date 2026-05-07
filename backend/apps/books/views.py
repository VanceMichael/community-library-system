from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Book
from .serializers import CategorySerializer, BookSerializer, BookListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'isbn', 'author', 'publisher']
    ordering_fields = ['title', 'author', 'created_at', 'available_copies']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        book = self.get_object()
        return Response({
            'id': book.id,
            'title': book.title,
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'status': book.status,
            'can_borrow': book.available_copies > 0
        })

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_books = Book.objects.filter(available_copies__gt=0)
        serializer = BookListSerializer(available_books, many=True)
        return Response(serializer.data)
