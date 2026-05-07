from rest_framework import serializers
from .models import PurchaseSuggestion, PurchaseOrder, PurchaseOrderItem


class PurchaseSuggestionSerializer(serializers.ModelSerializer):
    reader_name = serializers.SerializerMethodField()
    reader_id = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseSuggestion
        fields = [
            'id', 'reader', 'reader_name', 'reader_id', 'isbn', 'title',
            'author', 'publisher', 'publish_date', 'category', 'price',
            'reason', 'quantity', 'status', 'reviewed_by', 'reviewed_by_name',
            'review_date', 'review_comment', 'purchase_quantity', 'purchase_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'reader', 'status', 'reviewed_by', 'review_date', 'review_comment',
            'purchase_quantity', 'purchase_date', 'created_at', 'updated_at'
        ]

    def get_reader_name(self, obj):
        return obj.reader.name if obj.reader else None

    def get_reader_id(self, obj):
        return obj.reader.reader_id if obj.reader else None

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.username if obj.reviewed_by else None


class PurchaseSuggestionListSerializer(serializers.ModelSerializer):
    reader_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseSuggestion
        fields = [
            'id', 'title', 'isbn', 'author', 'reader_name',
            'status', 'quantity', 'created_at'
        ]

    def get_reader_name(self, obj):
        return obj.reader.name if obj.reader else None


class PurchaseSuggestionReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[('approved', '已批准'), ('rejected', '已拒绝')])
    review_comment = serializers.CharField(required=False, allow_blank=True)
    purchase_quantity = serializers.IntegerField(required=False, min_value=1)


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'purchase_suggestion', 'isbn', 'title',
            'author', 'publisher', 'quantity', 'unit_price', 'subtotal', 'remark'
        ]
        read_only_fields = ['purchase_order', 'subtotal']

    def validate(self, data):
        quantity = data.get('quantity', 0)
        unit_price = data.get('unit_price', 0)
        data['subtotal'] = quantity * unit_price
        return data


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, required=False)
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'contact_person', 'contact_phone',
            'total_amount', 'status', 'created_by', 'created_by_name',
            'approved_by', 'approved_by_name', 'approval_date', 'order_date',
            'receive_date', 'remark', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'order_number', 'total_amount', 'created_by', 'approval_date',
            'created_at', 'updated_at'
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.username if obj.approved_by else None

    def create(self, validated_data):
        from datetime import datetime
        import random

        items_data = validated_data.pop('items', [])

        order_number = f"PO{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        while PurchaseOrder.objects.filter(order_number=order_number).exists():
            order_number = f"PO{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

        validated_data['order_number'] = order_number
        validated_data['created_by'] = self.context['request'].user

        purchase_order = PurchaseOrder.objects.create(**validated_data)

        total_amount = 0
        for item_data in items_data:
            if 'subtotal' in item_data:
                del item_data['subtotal']
            quantity = item_data.get('quantity', 0)
            unit_price = item_data.get('unit_price', 0)
            subtotal = quantity * unit_price
            total_amount += subtotal
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, subtotal=subtotal, **item_data)

        purchase_order.total_amount = total_amount
        purchase_order.save()

        return purchase_order


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'total_amount',
            'status', 'created_by_name', 'created_at'
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None
