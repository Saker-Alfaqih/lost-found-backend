"""
Admin Panel App Models
Mapped from Flutter lib/models/admin_models.dart - Dashboard section
"""

from django.db import models


class DashboardStats(models.Model):
    """
    Cached dashboard statistics for admin panel
    Mapped from Flutter DashboardStats model in admin_models.dart
    """
    id = models.AutoField(primary_key=True)
    total_items = models.IntegerField(default=0)
    active_items = models.IntegerField(default=0)
    resolved_items = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    pending_reports = models.IntegerField(default=0)
    match_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    daily_trends = models.JSONField(default=list)  # List of {date, value} objects
    
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_stats'
        verbose_name_plural = 'Dashboard Stats'

    def __str__(self):
        return f"Stats - {self.last_updated}"