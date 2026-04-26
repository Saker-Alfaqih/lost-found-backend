"""
Users App Models
Mapped from Flutter lib/models/user.dart
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    GUEST = 'guest', 'Guest'
    USER = 'user', 'User'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


class UserStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'
    BANNED = 'banned', 'Banned'


class AuthProvider(models.TextChoices):
    EMAIL = 'email', 'Email'
    GOOGLE = 'google', 'Google'
    APPLE = 'apple', 'Apple'
    FACEBOOK = 'facebook', 'Facebook'


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Mapped from Flutter User model in user.dart
    """
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.URLField(max_length=500, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER)
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.ACTIVE)
    auth_provider = models.CharField(max_length=20, choices=AuthProvider.choices, default=AuthProvider.EMAIL)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def is_guest(self):
        return self.role == UserRole.GUEST

    @property
    def is_user(self):
        return self.role == UserRole.USER

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_active_status(self):
        return self.status == UserStatus.ACTIVE

    def can_access(self, required_role):
        """Check if user has required role or higher"""
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)