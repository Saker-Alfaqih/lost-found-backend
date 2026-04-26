"""
Support App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientSupportTicketViewSet, AdminSupportTicketViewSet

# Client Router
client_router = DefaultRouter()
client_router.register(r'tickets', ClientSupportTicketViewSet, basename='client-ticket')

# Admin Router
admin_router = DefaultRouter()
admin_router.register(r'tickets', AdminSupportTicketViewSet, basename='admin-ticket')

urlpatterns = [
    path('v1/client/', include(client_router.urls)),
    path('v1/admin/', include(admin_router.urls)),
]