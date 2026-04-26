"""
Matches App Views
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
import uuid

from .models import SmartMatch
from .serializers import (
    SmartMatchSerializer, SmartMatchAdminSerializer, SmartMatchUpdateSerializer
)

from apps.users.models import User, UserRole
from apps.items.models import Item
from apps.audit.models import AuditLog, AuditAction


# Permission Classes
class IsPlatformUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN]
        )


class IsPlatformAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN
        )


# Client Match ViewSet
class ClientMatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SmartMatch.objects.all()
    serializer_class = SmartMatchSerializer
    permission_classes = [IsPlatformUser]
    
    def get_queryset(self):
        user_items = Item.objects.filter(user_id=self.request.user.id).values_list('id', flat=True)
        return self.queryset.filter(
            Q(lost_item_id__in=user_items) | Q(found_item_id__in=user_items)
        ).filter(is_dismissed=False)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        match = self.get_object()
        match.is_dismissed = True
        match.save()
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.MATCH_DISMISSED,
            target_id=match.id,
            target_type='Match',
            description=f"User dismissed match {match.id}"
        )
        
        return Response({'message': 'Match dismissed'})


# Admin Match ViewSet
class AdminMatchViewSet(viewsets.ModelViewSet):
    queryset = SmartMatch.objects.all()
    permission_classes = [IsPlatformAdmin]
    serializer_class = SmartMatchAdminSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        
        match_type = self.request.query_params.get('match_type')
        is_reviewed = self.request.query_params.get('is_reviewed')
        
        if match_type:
            queryset = queryset.filter(match_type=match_type)
        if is_reviewed is not None:
            queryset = queryset.filter(is_reviewed=is_reviewed.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        match = self.get_object()
        match.is_reviewed = True
        match.save()
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.MATCH_APPROVED,
            target_id=match.id,
            target_type='Match',
            description=f"Admin approved match {match.id}",
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'Match approved'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip