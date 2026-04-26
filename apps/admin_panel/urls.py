"""
Admin Panel App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminDashboardViewSet, AdminAuditLogViewSet

# Admin Router
admin_router = DefaultRouter()
admin_router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')
admin_router.register(r'audit-logs', AdminAuditLogViewSet, basename='admin-audit-log')

urlpatterns = [
    path('v1/admin/', include(admin_router.urls)),
]