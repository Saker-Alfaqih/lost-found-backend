"""
Support App Views
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid

from .models import SupportTicket, TicketStatus
from .serializers import (
    SupportTicketCreateSerializer, SupportTicketListSerializer,
    SupportTicketDetailSerializer, SupportTicketUpdateSerializer,
    TicketMessageSerializer, TicketMessageCreateSerializer
)

from apps.users.models import User, UserRole
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


# Client Support Ticket ViewSet
class ClientSupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    permission_classes = [IsPlatformUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SupportTicketCreateSerializer
        if self.action == 'list':
            return SupportTicketListSerializer
        return SupportTicketDetailSerializer
    
    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)
    
    @action(detail=True, methods=['post'], permission_classes=[IsPlatformUser])
    def add_message(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketMessageCreateSerializer(
            data=request.data,
            context={'request': request, 'ticket_id': ticket.id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Support Ticket ViewSet
class AdminSupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    permission_classes = [IsPlatformAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SupportTicketListSerializer
        if self.action in ['update', 'partial_update']:
            return SupportTicketUpdateSerializer
        return SupportTicketDetailSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        ticket.assigned_admin_id = request.user.id
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.save()
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.TICKET_ASSIGNED,
            target_id=ticket.id,
            target_type='Ticket',
            description=f"Admin {request.user.name} assigned to ticket {ticket.ticket_number}",
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'Ticket assigned'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = TicketStatus.RESOLVED
        ticket.save()
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.TICKET_RESOLVED,
            target_id=ticket.id,
            target_type='Ticket',
            description=f"Admin resolved ticket {ticket.ticket_number}",
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'Ticket resolved'})
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketMessageCreateSerializer(
            data=request.data,
            context={'request': request, 'ticket_id': ticket.id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip