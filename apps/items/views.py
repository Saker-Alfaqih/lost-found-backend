"""
Items App Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
import uuid

from .models import Item, ItemStatus, ItemType
from .serializers import (
    ItemCreateSerializer, ItemListSerializer, ItemDetailSerializer,
    ItemUpdateSerializer, ItemAdminUpdateSerializer
)

from apps.users.models import User, UserRole
from apps.matches.models import SmartMatch
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


# Client Item ViewSet
class ClientItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [IsPlatformUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ItemCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ItemUpdateSerializer
        if self.action == 'list':
            return ItemListSerializer
        return ItemDetailSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = self.queryset
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(keywords__icontains=search)
            )
        
        if self.request.method in ['PUT', 'PATCH', 'DELETE'] and self.request.user.role == UserRole.USER:
            queryset = queryset.filter(user_id=self.request.user.id)
        
        return queryset.filter(status=ItemStatus.ACTIVE)
    
    @action(detail=False, methods=['get'])
    def my_items(self, request):
        items = self.queryset.filter(user_id=request.user.id)
        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.queryset.filter(status=ItemStatus.ACTIVE)
        
        q = self.request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(keywords__icontains=q)
            )
        
        item_type = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')
        
        if item_type:
            queryset = queryset.filter(type=item_type)
        if category:
            queryset = queryset.filter(category=category)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        serializer = ItemListSerializer(queryset, many=True)
        return Response(serializer.data)


# Admin Item ViewSet
class AdminItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [IsPlatformAdmin]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ItemAdminUpdateSerializer
        if self.action == 'list':
            return ItemListSerializer
        return ItemDetailSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        
        status_filter = self.request.query_params.get('status')
        type_filter = self.request.query_params.get('type')
        category_filter = self.request.query_params.get('category')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        item_ids = request.data.get('item_ids', [])
        new_status = request.data.get('status')
        
        items = Item.objects.filter(id__in=item_ids)
        count = items.update(status=new_status)
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.BULK_ITEMS_CLOSED if new_status == ItemStatus.RESOLVED else AuditAction.BULK_ITEMS_ARCHIVED,
            description=f"Bulk updated {count} items to {new_status}",
            new_values={'item_ids': item_ids, 'status': new_status},
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': f'Updated {count} items'})
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        item_ids = request.data.get('item_ids', [])
        count = Item.objects.filter(id__in=item_ids).delete()[0]
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.BULK_ITEMS_DELETED,
            description=f"Bulk deleted {count} items",
            new_values={'item_ids': item_ids},
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': f'Deleted {count} items'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip