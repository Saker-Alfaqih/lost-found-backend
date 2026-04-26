"""
Users App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientUserViewSet, AdminUserViewSet

# Client Router
client_router = DefaultRouter()
client_router.register(r'', ClientUserViewSet, basename='client-user')

# Admin Router
admin_router = DefaultRouter()
admin_router.register(r'', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('v1/client/', include(client_router.urls)),
    path('v1/admin/', include(admin_router.urls)),
]