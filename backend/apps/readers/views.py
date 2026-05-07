from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Reader
from .serializers import ReaderSerializer, ReaderListSerializer, ReaderCreateSerializer


class ReaderViewSet(viewsets.ModelViewSet):
    queryset = Reader.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'gender']
    search_fields = ['reader_id', 'name', 'phone', 'id_card']
    ordering_fields = ['name', 'reader_id', 'register_date', 'borrow_count']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReaderListSerializer
        elif self.action == 'create':
            return ReaderCreateSerializer
        return ReaderSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        reader = getattr(user, 'reader', None)
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        if reader:
            data.update({
                'reader_id': reader.reader_id,
                'reader_pk': reader.id,
                'name': reader.name,
                'phone': reader.phone,
                'gender': reader.gender,
                'is_reader': True,
            })
        else:
            data['is_reader'] = False
        return Response(data)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        reader = self.get_object()
        user = reader.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'error': '请输入旧密码和新密码'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'error': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 3:
            return Response({'error': '新密码长度不能少于3位'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': '密码修改成功'})

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        reader = self.get_object()
        if reader.status == 'suspended':
            return Response({'error': '读者证已挂失'}, status=status.HTTP_400_BAD_REQUEST)
        reader.status = 'suspended'
        reader.save()
        return Response({'message': '读者证已挂失', 'status': reader.status})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        reader = self.get_object()
        if reader.status == 'active':
            return Response({'error': '读者证已处于正常状态'}, status=status.HTTP_400_BAD_REQUEST)
        if reader.status == 'closed':
            return Response({'error': '已注销的读者证无法激活'}, status=status.HTTP_400_BAD_REQUEST)
        reader.status = 'active'
        reader.save()
        return Response({'message': '读者证已激活', 'status': reader.status})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        reader = self.get_object()
        if reader.status == 'closed':
            return Response({'error': '读者证已注销'}, status=status.HTTP_400_BAD_REQUEST)
        if reader.borrow_count > 0:
            return Response({'error': f'读者还有 {reader.borrow_count} 本图书未归还'}, status=status.HTTP_400_BAD_REQUEST)
        reader.status = 'closed'
        reader.save()
        return Response({'message': '读者证已注销', 'status': reader.status})

    @action(detail=True, methods=['get'])
    def check_borrow_eligibility(self, request, pk=None):
        reader = self.get_object()
        can_borrow, message = reader.can_borrow()
        return Response({
            'can_borrow': can_borrow,
            'message': message,
            'borrow_limit': reader.borrow_limit,
            'current_borrows': reader.borrow_count
        })
