"""
Matches App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientMatchViewSet, AdminMatchViewSet

# Client Router
client_router = DefaultRouter()
client_router.register(r'', ClientMatchViewSet, basename='client-match')

# Admin Router
admin_router = DefaultRouter()
admin_router.register(r'', AdminMatchViewSet, basename='admin-match')

urlpatterns = [
    path('v1/client/', include(client_router.urls)),
    path('v1/admin/', include(admin_router.urls)),
]