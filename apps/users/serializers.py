"""
Users App Serializers
"""

from rest_framework import serializers
from .models import User, UserRole, AuthProvider


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'password', 'auth_provider']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        import uuid
        validated_data['id'] = str(uuid.uuid4())
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone', 'profile_image',
            'role', 'status', 'is_email_verified', 'created_at',
            'last_login_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'status', 'created_at']


class UserListSerializer(serializers.ModelSerializer):
    """Minimal serializer for user lists"""
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Full user serializer"""
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'last_login_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    class Meta:
        model = User
        fields = ['name', 'phone', 'profile_image', 'role', 'status', 'is_email_verified']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class SocialLoginSerializer(serializers.Serializer):
    """Serializer for social login"""
    provider = serializers.ChoiceField(choices=AuthProvider.choices)
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    name = serializers.CharField(required=False)