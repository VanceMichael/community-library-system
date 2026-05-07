from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from .models import PurchaseSuggestion, PurchaseOrder, PurchaseOrderItem
from apps.books.models import Book, Category
from .serializers import (
    PurchaseSuggestionSerializer, PurchaseSuggestionListSerializer,
    PurchaseSuggestionReviewSerializer, PurchaseOrderSerializer,
    PurchaseOrderListSerializer
)


class PurchaseSuggestionViewSet(viewsets.ModelViewSet):
    queryset = PurchaseSuggestion.objects.select_related('reader', 'reviewed_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'reader']
    search_fields = ['title', 'isbn', 'author', 'publisher', 'reader__name']
    ordering_fields = ['created_at', 'status', 'quantity']

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseSuggestionListSerializer
        elif self.action == 'review':
            return PurchaseSuggestionReviewSerializer
        return PurchaseSuggestionSerializer

    def perform_create(self, serializer):
        reader = getattr(self.request.user, 'reader', None)
        if not reader:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('用户不是读者，无法提交采购建议')
        serializer.save(reader=reader)

    @action(detail=False, methods=['get'])
    def my_suggestions(self, request):
        reader = getattr(request.user, 'reader', None)
        if not reader:
            return Response({'error': '用户不是读者'}, status=status.HTTP_400_BAD_REQUEST)
        suggestions = PurchaseSuggestion.objects.filter(reader=reader)
        serializer = PurchaseSuggestionListSerializer(suggestions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({'error': '只有管理员才能审核采购建议'}, status=status.HTTP_403_FORBIDDEN)

        suggestion = self.get_object()

        if suggestion.status != 'pending':
            return Response({'error': '该建议已审核'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PurchaseSuggestionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_val = serializer.validated_data['status']
        review_comment = serializer.validated_data.get('review_comment', '')
        purchase_quantity = serializer.validated_data.get('purchase_quantity')

        with transaction.atomic():
            suggestion.status = status_val
            suggestion.reviewed_by = request.user
            suggestion.review_date = timezone.now()
            suggestion.review_comment = review_comment
            if purchase_quantity:
                suggestion.purchase_quantity = purchase_quantity
            suggestion.save()

        return Response(PurchaseSuggestionSerializer(suggestion).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        suggestion = self.get_object()

        if suggestion.status != 'pending':
            return Response({'error': '只能取消待审核的建议'}, status=status.HTTP_400_BAD_REQUEST)

        reader = getattr(request.user, 'reader', None)
        if not request.user.is_staff and not request.user.is_superuser:
            if not reader or suggestion.reader.id != reader.id:
                return Response({'error': '只能取消自己提交的建议'}, status=status.HTTP_403_FORBIDDEN)

        suggestion.status = 'cancelled'
        suggestion.save()

        return Response(PurchaseSuggestionSerializer(suggestion).data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related('created_by', 'approved_by').prefetch_related('items').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['order_number', 'supplier', 'contact_person']
    ordering_fields = ['created_at', 'total_amount', 'order_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except Exception as e:
            import traceback
            print(f"Error creating purchase order: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def approved_suggestions(self, request):
        from django.db.models import Q, Exists, OuterRef
        active_order_items = PurchaseOrderItem.objects.filter(
            purchase_suggestion=OuterRef('pk'),
            purchase_order__status__in=['draft', 'submitted', 'approved', 'ordered', 'received']
        )
        suggestions = PurchaseSuggestion.objects.filter(
            status='approved'
        ).exclude(
            Exists(active_order_items)
        ).select_related('reader').distinct()
        serializer = PurchaseSuggestionSerializer(suggestions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        order = self.get_object()

        if order.status != 'draft':
            return Response({'error': '只能提交草稿状态的订单'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'submitted'
        order.save()

        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        order = self.get_object()

        if order.status != 'submitted':
            return Response({'error': '只能审批已提交的订单'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'approved'
        order.approved_by = request.user
        order.approval_date = timezone.now()
        order.save()

        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def order(self, request, pk=None):
        order = self.get_object()

        if order.status != 'approved':
            return Response({'error': '只能对已批准的订单进行订购'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'ordered'
        order.order_date = timezone.now().date()
        order.save()

        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        order = self.get_object()

        if order.status != 'ordered':
            return Response({'error': '只能对已订购的订单进行到货确认'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order.status = 'received'
            order.receive_date = timezone.now().date()
            order.save()

            for item in order.items.all():
                category, _ = Category.objects.get_or_create(
                    name=item.publisher or '未分类',
                    defaults={'code': f"CAT{timezone.now().strftime('%Y%m%d%H%M%S')}"}
                )

                book, created = Book.objects.update_or_create(
                    isbn=item.isbn,
                    defaults={
                        'title': item.title,
                        'author': item.author,
                        'publisher': item.publisher,
                        'category': category,
                        'location': '待上架',
                        'total_copies': item.quantity,
                        'available_copies': item.quantity,
                        'price': item.unit_price,
                        'status': 'available'
                    }
                )

                if not created:
                    book.total_copies += item.quantity
                    book.available_copies += item.quantity
                    book.save()

                if item.purchase_suggestion:
                    item.purchase_suggestion.status = 'purchased'
                    item.purchase_suggestion.purchase_date = timezone.now().date()
                    item.purchase_suggestion.save()

        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status not in ['draft', 'submitted']:
            return Response({'error': '只能取消草稿或已提交状态的订单'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()

        return Response(PurchaseOrderSerializer(order).data)
