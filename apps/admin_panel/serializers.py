"""
Admin Panel App Serializers
"""

from rest_framework import serializers
from .models import DashboardStats


class AuditLogSerializer(serializers.Serializer):
    """Serializer for audit logs"""
    id = serializers.CharField()
    admin_id = serializers.CharField()
    admin_name = serializers.CharField()
    action = serializers.CharField()
    target_id = serializers.CharField()
    target_type = serializers.CharField()
    description = serializers.CharField()
    old_values = serializers.JSONField()
    new_values = serializers.JSONField()
    ip_address = serializers.IPAddressField()
    user_agent = serializers.CharField()
    created_at = serializers.DateTimeField()


class ChartDataPointSerializer(serializers.Serializer):
    """Serializer for chart data points"""
    date = serializers.DateField()
    value = serializers.FloatField()


class DashboardStatsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard statistics"""
    daily_trends = ChartDataPointSerializer(many=True, read_only=True)
    
    class Meta:
        model = DashboardStats
        fields = '__all__'