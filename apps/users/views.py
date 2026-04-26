"""
Users App Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from datetime import datetime
import uuid

from .models import User, UserRole, UserStatus
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserListSerializer,
    UserDetailSerializer, UserUpdateSerializer,
    LoginSerializer, SocialLoginSerializer
)

# Import from other apps
from apps.items.models import Item, ItemStatus
from apps.matches.models import SmartMatch
from apps.audit.models import AuditLog, AuditAction
from apps.support.models import SupportTicket, TicketStatus


# Custom Permission Classes
class IsPlatformAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN
        )


class IsPlatformUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN]
        )


class IsActiveUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.status == UserStatus.ACTIVE
        )


# Client User ViewSet
class ClientUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsPlatformUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserProfileSerializer
    
    def get_queryset(self):
        if self.request.user.role == UserRole.USER:
            return User.objects.filter(id=self.request.user.id)
        return self.queryset
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(username=email, password=password)
            if user:
                if user.status != UserStatus.ACTIVE:
                    return Response({'error': 'Account is not active'}, status=status.HTTP_403_FORBIDDEN)
                
                user.last_login_at = datetime.now()
                user.save()
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserProfileSerializer(user).data
                })
            
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def social_login(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        if serializer.is_valid():
            provider = serializer.validated_data['provider']
            token = serializer.validated_data['token']
            email = serializer.validated_data.get('email')
            name = serializer.validated_data.get('name')
            
            try:
                user = User.objects.get(email=email)
                user.auth_provider = provider
                user.save()
            except User.DoesNotExist:
                user = User.objects.create(
                    id=str(uuid.uuid4()),
                    email=email,
                    name=name or email.split('@')[0],
                    auth_provider=provider,
                    is_email_verified=True
                )
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Admin User ViewSet
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsPlatformAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserDetailSerializer
    
    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        user = self.get_object()
        user.status = UserStatus.BANNED
        user.save()
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.USER_BANNED,
            target_id=user.id,
            target_type='User',
            description=f"Admin banned user {user.email}",
            old_values={'status': user.status},
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'User banned successfully'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.status = UserStatus.ACTIVE
        user.save()
        
        AuditLog.objects.create(
            id=str(uuid.uuid4()),
            admin_id=request.user.id,
            admin_name=request.user.name,
            action=AuditAction.USER_ACTIVATED,
            target_id=user.id,
            target_type='User',
            description=f"Admin activated user {user.email}",
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'User activated successfully'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip