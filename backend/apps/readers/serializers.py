from rest_framework import serializers
from .models import Reader


class ReaderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Reader
        fields = [
            'id', 'reader_id', 'name', 'gender', 'phone', 'email',
            'address', 'id_card', 'status', 'borrow_limit', 'borrow_count',
            'register_date', 'expire_date', 'photo', 'username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reader_id', 'borrow_count', 'register_date', 'created_at', 'updated_at']


class ReaderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = [
            'id', 'reader_id', 'name', 'phone', 'status',
            'borrow_limit', 'borrow_count', 'register_date'
        ]


class ReaderCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = Reader
        fields = [
            'username', 'password', 'name', 'gender', 'phone', 'email',
            'address', 'id_card', 'borrow_limit', 'expire_date', 'photo'
        ]

    def create(self, validated_data):
        from django.contrib.auth.models import User
        from datetime import datetime
        import random
        import string

        username = validated_data.pop('username')
        password = validated_data.pop('password', None)
        email = validated_data.pop('email', '')

        user = User.objects.create_user(username=username, email=email)
        if password:
            user.set_password(password)
        else:
            password = ''.join(random.choices(string.digits, k=6))
            user.set_password(password)
        user.save()

        reader_id = f"R{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        while Reader.objects.filter(reader_id=reader_id).exists():
            reader_id = f"R{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

        reader = Reader.objects.create(
            user=user,
            reader_id=reader_id,
            **validated_data
        )
        return reader
