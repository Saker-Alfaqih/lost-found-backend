"""
Items App Serializers
"""

from rest_framework import serializers
from .models import Item, ItemType, ItemStatus, ItemCategory


class ItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating items"""
    class Meta:
        model = Item
        fields = [
            'id', 'reference_number', 'type', 'category', 'title',
            'description', 'location', 'latitude', 'longitude', 'date',
            'time', 'images', 'keywords', 'reward'
        ]
        read_only_fields = ['id', 'reference_number', 'status']

    def create(self, validated_data):
        import uuid
        from datetime import datetime
        
        user = self.context['request'].user
        
        validated_data['id'] = str(uuid.uuid4())
        validated_data['reference_number'] = f"ITEM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        validated_data['user_id'] = user.id
        validated_data['user_name'] = user.name
        validated_data['user_phone'] = user.phone
        validated_data['user_email'] = user.email
        
        return super().create(validated_data)


class ItemListSerializer(serializers.ModelSerializer):
    """Minimal serializer for item lists"""
    class Meta:
        model = Item
        fields = [
            'id', 'reference_number', 'type', 'status', 'category',
            'title', 'location', 'date', 'reward', 'created_at'
        ]


class ItemDetailSerializer(serializers.ModelSerializer):
    """Full item serializer"""
    class Meta:
        model = Item
        fields = '__all__'


class ItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating items"""
    class Meta:
        model = Item
        fields = [
            'title', 'description', 'location', 'latitude', 'longitude',
            'date', 'time', 'images', 'keywords', 'reward', 'status'
        ]


class ItemAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin updates on items"""
    class Meta:
        model = Item
        fields = ['status', 'category']