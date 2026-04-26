"""
Admin Panel App Views
"""

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Count
from datetime import datetime, timedelta

from .models import DashboardStats
from .serializers import DashboardStatsSerializer, AuditLogSerializer

from apps.users.models import User, UserRole
from apps.items.models import Item, ItemStatus
from apps.matches.models import SmartMatch
from apps.support.models import SupportTicket, TicketStatus
from apps.audit.models import AuditLog


# Permission Classes
class IsPlatformAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN
        )


# Admin Dashboard ViewSet
class AdminDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsPlatformAdmin]
    
    def list(self, request):
        stats, created = DashboardStats.objects.get_or_create(id=1)
        
        total_items = Item.objects.count()
        active_items = Item.objects.filter(status=ItemStatus.ACTIVE).count()
        resolved_items = Item.objects.filter(status=ItemStatus.RESOLVED).count()
        total_users = User.objects.count()
        pending_reports = SupportTicket.objects.filter(status=TicketStatus.OPEN).count()
        
        total_matches = SmartMatch.objects.count()
        resolved_matches = SmartMatch.objects.filter(is_reviewed=True).count()
        match_success_rate = (resolved_matches / total_matches * 100) if total_matches > 0 else 0.0
        
        daily_trends = []
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            items_count = Item.objects.filter(created_at__date=date).count()
            daily_trends.append({
                'date': date,
                'value': items_count
            })
        
        stats.total_items = total_items
        stats.active_items = active_items
        stats.resolved_items = resolved_items
        stats.total_users = total_users
        stats.pending_reports = pending_reports
        stats.match_success_rate = match_success_rate
        stats.daily_trends = daily_trends
        stats.save()
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


# Admin Audit Log ViewSet
class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsPlatformAdmin]
    
    def get_queryset(self):
        queryset = self.queryset
        
        action_filter = self.request.query_params.get('action')
        admin_id = self.request.query_params.get('admin_id')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        if admin_id:
            queryset = queryset.filter(admin_id=admin_id)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset