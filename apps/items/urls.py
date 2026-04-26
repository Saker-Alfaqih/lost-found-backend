"""
Items App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientItemViewSet, AdminItemViewSet

# Client Router
client_router = DefaultRouter()
client_router.register(r'', ClientItemViewSet, basename='client-item')

# Admin Router
admin_router = DefaultRouter()
admin_router.register(r'', AdminItemViewSet, basename='admin-item')

urlpatterns = [
    path('v1/client/', include(client_router.urls)),
    path('v1/admin/', include(admin_router.urls)),
]