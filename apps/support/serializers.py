"""
Support App Serializers
"""

from rest_framework import serializers
from .models import SupportTicket, TicketMessage, TicketStatus, TicketPriority


class TicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for ticket messages"""
    class Meta:
        model = TicketMessage
        fields = ['id', 'sender_id', 'sender_name', 'is_admin', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating support tickets"""
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'type', 'priority', 'subject',
            'description', 'related_item_id'
        ]
        read_only_fields = ['id', 'ticket_number', 'status', 'assigned_admin_id']
    
    def create(self, validated_data):
        import uuid
        from datetime import datetime
        
        user = self.context['request'].user
        
        validated_data['id'] = str(uuid.uuid4())
        validated_data['ticket_number'] = f"TKT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        validated_data['user_id'] = user.id
        validated_data['user_name'] = user.name
        validated_data['user_email'] = user.email
        
        return super().create(validated_data)


class SupportTicketListSerializer(serializers.ModelSerializer):
    """Minimal serializer for ticket lists"""
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'user_name', 'user_email',
            'type', 'priority', 'status', 'subject', 'created_at'
        ]


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    """Full ticket serializer with messages"""
    messages = TicketMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = '__all__'


class SupportTicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tickets"""
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_admin_id']


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding messages to tickets"""
    class Meta:
        model = TicketMessage
        fields = ['id', 'content']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        import uuid
        request = self.context['request']
        ticket_id = self.context['ticket_id']
        
        validated_data['id'] = str(uuid.uuid4())
        validated_data['ticket_id'] = ticket_id
        validated_data['sender_id'] = request.user.id
        validated_data['sender_name'] = request.user.name
        validated_data['is_admin'] = request.user.role in ['admin', 'moderator']
        
        return super().create(validated_data)